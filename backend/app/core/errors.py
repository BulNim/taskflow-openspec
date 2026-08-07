from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# 라우터에서 의도적으로 던지는 도메인 에러. 모든 API 에러 응답을
# { error: { code, message, meta? } } 형태로 표준화하기 위해 사용한다.
class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, meta: dict | None = None):
        self.status_code = status_code
        self.code = code  # SCREAMING_SNAKE 형태의 기계 판독용 코드 (예: EMAIL_TAKEN)
        self.message = message  # 사용자에게 그대로 노출되는 한국어 메시지
        self.meta = meta  # limit/actual 등 부가 컨텍스트 (선택)

    def body(self):
        error = {"code": self.code, "message": self.message}
        if self.meta:
            error["meta"] = self.meta
        return {"error": error}


def register_error_handlers(app: FastAPI):
    # 1) 라우터에서 명시적으로 던진 AppError - 그대로 표준 형태로 직렬화
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content=exc.body())

    # 2) pydantic 요청 바디 검증 실패 - 400 VALIDATION_ERROR로 통일
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "VALIDATION_ERROR", "message": "요청 형식이 올바르지 않습니다"}},
        )

    # 3) 그 외 예기치 못한 모든 예외 - 내부 정보를 노출하지 않고 500으로 통일
    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "서버 오류가 발생했습니다"}},
        )
