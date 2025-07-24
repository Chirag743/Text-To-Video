# Text To Video Web App

A full-stack AI-powered web application that converts your text or topic into engaging videos. Built with React (Vite) for the frontend and FastAPI for the backend.

---

## Features

- Enter a topic or your own script to generate a video
- AI-powered script generation from topic
- Download generated videos
- Modern UI with Tailwind CSS

---

## Project Structure

```
text-to-video/
├── client/   # React + Vite frontend
├── server/   # FastAPI backend
└── README.md
```

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/Chirag743/Text-To-Video.git
cd text-to-video
```

---

### 2. Setup the Backend (FastAPI)

```sh
cd server
# Create and activate a new conda environment (recommended)
conda create -n text2video python=3.10
conda activate text2video

# Install all required Python packages
pip install -r requirements.txt

# Run the FastAPI server
uvicorn index:app --reload
```

- Configure your API keys in `server/routes/router.py` as needed.
- Videos will be saved in the `videos/` directory.

---

### 3. Setup the Frontend (React + Vite)

```sh
cd ../client
npm install
npm run dev
```

- Update API URLs in the frontend if deploying to production.

---

## Deployment

- Build the frontend: `npm run build` (output in `client/dist`)
- Serve static files and videos from FastAPI (see `server/index.py`)
- Deploy both client and server to your preferred cloud provider

---

## Usage

1. Go to the home page and click **Get Started**
2. Enter your project name and topic
3. Choose to enter your own script or generate one from the topic
4. Click **Generate Video** and download your result

---

## License

MIT

---

## Credits

- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [MoviePy](https://zulko.github.io/moviepy/)
- [Google Generative AI](https://ai.google.dev/)