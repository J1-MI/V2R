"""
ML 우선순위 모델
XGBoost를 사용하여 취약점의 우선순위를 예측합니다.
"""

import logging
import pickle
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import pandas as pd

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available, using rule-based fallback")

from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class PriorityModel:
    """취약점 우선순위 예측 모델"""

    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: 저장된 모델 파일 경로 (None이면 새로 학습)
        """
        self.model = None
        self.model_path = model_path or str(PROJECT_ROOT / "models" / "priority_model.pkl")
        self.feature_names = [
            "severity_score",      # 심각도 점수 (Critical=4, High=3, Medium=2, Low=1, Info=0)
            "reliability_score",   # 신뢰도 점수 (0-100)
            "cve_count",           # CVE 개수
            "has_poc",             # PoC 존재 여부 (1 or 0)
            "poc_success",         # PoC 재현 성공 여부 (1 or 0)
            "days_since_discovery" # 발견 후 경과 일수
        ]
        
        if XGBOOST_AVAILABLE:
            if model_path and Path(model_path).exists():
                self.load_model(model_path)
            else:
                self.model = self._create_default_model()
        else:
            logger.warning("XGBoost not available, using rule-based model")

    def _create_default_model(self) -> Optional[Any]:
        """기본 모델 생성 (간단한 규칙 기반)"""
        if not XGBOOST_AVAILABLE:
            return None
        
        # 간단한 XGBoost 모델 생성 (기본 파라미터)
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='multi:softprob',
            num_class=5  # 우선순위 1-5
        )
        return model

    def extract_features(self, vulnerability: Dict[str, Any]) -> np.ndarray:
        """
        취약점 데이터에서 특징 추출

        Args:
            vulnerability: 취약점 정보 딕셔너리

        Returns:
            특징 벡터
        """
        # 심각도 점수
        severity_map = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1,
            "Info": 0
        }
        severity = vulnerability.get("severity", "Info")
        severity_score = severity_map.get(severity, 0)

        # 신뢰도 점수
        reliability_score = vulnerability.get("reliability_score", 0) or 0
        reliability_score = max(0, min(100, reliability_score))  # 0-100 범위로 제한

        # CVE 개수
        cve_list = vulnerability.get("cve_list", [])
        cve_count = len(cve_list) if isinstance(cve_list, list) else 0

        # PoC 존재 여부
        has_poc = 1 if vulnerability.get("poc_id") or vulnerability.get("has_poc") else 0

        # PoC 재현 성공 여부
        poc_status = vulnerability.get("poc_status", "")
        poc_success = 1 if poc_status == "success" else 0

        # 발견 후 경과 일수 (간단히 0으로 설정, 실제로는 timestamp 계산 필요)
        days_since_discovery = vulnerability.get("days_since_discovery", 0)

        features = np.array([
            severity_score,
            reliability_score / 100.0,  # 0-1 범위로 정규화
            min(cve_count, 10) / 10.0,  # 0-1 범위로 정규화
            has_poc,
            poc_success,
            min(days_since_discovery, 365) / 365.0  # 0-1 범위로 정규화
        ])

        return features

    def predict_priority(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        취약점의 우선순위 예측

        Args:
            vulnerability: 취약점 정보 딕셔너리

        Returns:
            우선순위 예측 결과 (priority: 1-5, score: 0-100)
        """
        if not XGBOOST_AVAILABLE or self.model is None:
            # 규칙 기반 fallback
            return self._rule_based_priority(vulnerability)

        try:
            features = self.extract_features(vulnerability)
            features_2d = features.reshape(1, -1)

            # 우선순위 예측 (1-5, 1이 가장 높은 우선순위)
            if hasattr(self.model, 'predict_proba'):
                # 확률 기반 예측
                proba = self.model.predict_proba(features_2d)[0]
                priority = np.argmax(proba) + 1  # 1-5
                confidence = float(np.max(proba)) * 100
            else:
                # 직접 예측
                priority = int(self.model.predict(features_2d)[0]) + 1
                confidence = 50.0  # 기본값

            # 우선순위 점수 계산 (1-5를 0-100으로 변환: 1=100, 5=20)
            priority_score = 100 - ((priority - 1) * 20)

            return {
                "priority": priority,
                "priority_score": priority_score,
                "confidence": confidence,
                "features": features.tolist()
            }

        except Exception as e:
            logger.error(f"우선순위 예측 실패: {str(e)}")
            return self._rule_based_priority(vulnerability)

    def _rule_based_priority(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        규칙 기반 우선순위 계산 (XGBoost 없을 때 fallback)

        Args:
            vulnerability: 취약점 정보

        Returns:
            우선순위 결과
        """
        severity = vulnerability.get("severity", "Info")
        reliability_score = vulnerability.get("reliability_score", 0) or 0
        has_poc = vulnerability.get("poc_id") or vulnerability.get("has_poc", False)
        poc_success = vulnerability.get("poc_status") == "success"

        # 우선순위 계산 로직
        if severity == "Critical" and (reliability_score >= 80 or poc_success):
            priority = 1
        elif severity == "Critical" or (severity == "High" and poc_success):
            priority = 2
        elif severity == "High" or (severity == "Medium" and reliability_score >= 60):
            priority = 3
        elif severity == "Medium" or (severity == "Low" and has_poc):
            priority = 4
        else:
            priority = 5

        priority_score = 100 - ((priority - 1) * 20)

        return {
            "priority": priority,
            "priority_score": priority_score,
            "confidence": 70.0,  # 규칙 기반이므로 중간 신뢰도
            "method": "rule_based"
        }

    def train(self, training_data: List[Dict[str, Any]], labels: List[int]):
        """
        모델 학습

        Args:
            training_data: 학습 데이터 (취약점 정보 리스트)
            labels: 우선순위 레이블 (1-5)
        """
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, cannot train model")
            return False

        try:
            # 특징 추출
            X = np.array([self.extract_features(vuln) for vuln in training_data])
            y = np.array(labels)

            # 모델 학습
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                objective='multi:softprob',
                num_class=5
            )
            self.model.fit(X, y)

            # 모델 저장
            self.save_model(self.model_path)
            logger.info(f"모델 학습 완료 및 저장: {self.model_path}")

            return True

        except Exception as e:
            logger.error(f"모델 학습 실패: {str(e)}")
            return False

    def save_model(self, path: str):
        """모델 저장"""
        if self.model is None:
            logger.warning("저장할 모델이 없습니다")
            return False

        try:
            model_dir = Path(path).parent
            model_dir.mkdir(parents=True, exist_ok=True)

            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"모델 저장 완료: {path}")
            return True

        except Exception as e:
            logger.error(f"모델 저장 실패: {str(e)}")
            return False

    def load_model(self, path: str):
        """모델 로드"""
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"모델 로드 완료: {path}")
            return True

        except Exception as e:
            logger.error(f"모델 로드 실패: {str(e)}")
            return False

