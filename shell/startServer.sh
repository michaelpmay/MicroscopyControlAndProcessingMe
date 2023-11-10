 uvicorn automation_service:app --reload --port 8000 --timeout-keep-alive 100000 --ws-max-size 0 &
 uvicorn processing_service:app --reload --port 8001 --timeout-keep-alive 100000 --ws-max-size 0 &
