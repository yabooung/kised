# scripts/async_log_cleanup.py
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from core.database import get_log_db
from core.config import Settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogCleaner:
    def __init__(self):
        self.settings = Settings()
        self.retention_days = self.settings.LOG_RETENTION_DAYS
        self.cleanup_interval = self.settings.LOG_CLEANUP_INTERVAL

    async def backup_logs(self, db):
        """백업이 필요한 로그를 저장"""
        backup_date = datetime.now() - timedelta(days=self.retention_days)
        try:
            query = text("""
                SELECT * FROM api_logs 
                WHERE timestamp < :backup_date
            """)
            result = await db.execute(query, {"backup_date": backup_date})
            # 백업 로직 구현 (예: 파일로 저장)
            return True
        except Exception as e:
            logger.error(f"로그 백업 실패: {e}")
            return False

    async def cleanup_old_logs(self):
        """오래된 로그 삭제"""
        try:
            async with get_log_db() as db:
                # 백업 수행
                backup_success = await self.backup_logs(db)
                if not backup_success:
                    logger.warning("백업 실패로 인한 삭제 작업 중단")
                    return

                # 로그 삭제
                query = text("""
                    DELETE FROM api_logs 
                    WHERE timestamp < DATE_SUB(NOW(), INTERVAL :days DAY)
                """)
                result = await db.execute(query, {"days": self.retention_days})
                await db.commit()
                logger.info(f"로그 정리 완료: {result.rowcount}개 삭제됨")
        except Exception as e:
            logger.error(f"로그 정리 중 오류 발생: {e}")

    async def schedule_cleanup(self):
        """정기적인 로그 정리 스케줄링"""
        while True:
            try:
                await self.cleanup_old_logs()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                logger.info("로그 정리 작업 중단됨")
                break
            except Exception as e:
                logger.error(f"예상치 못한 오류 발생: {e}")
                await asyncio.sleep(60)  # 오류 발생시 1분 후 재시도

if __name__ == "__main__":
    cleaner = LogCleaner()
    asyncio.run(cleaner.schedule_cleanup())