module.exports = {
  apps: [
    {
      name: "fastapi-server",
      script: "uvicorn",
      args: "main:app --host 0.0.0.0 --port 8000 --workers 4",
      interpreter: "python3",
      watch: true,
      ignore_watch: [
        "videos",
        "__pycache__",
        "*.mp3",
        "*.mp4"
      ]
    }
  ]
};
