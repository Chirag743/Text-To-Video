import React from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate("/form"); // Change "/form" to your actual form route
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-blue-100 to-purple-200">
      <div className="bg-white rounded-xl shadow-2xl p-10 max-w-lg w-full text-center">
        <h1 className="text-4xl font-bold text-blue-700 mb-4">Text To Video</h1>
        <p className="text-gray-600 mb-8">
          Instantly turn your ideas into engaging videos! Enter your topic or script and let our AI generate a video for you.
        </p>
        <button
          onClick={handleGetStarted}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold text-lg shadow hover:bg-blue-700 transition"
        >
          Get Started
        </button>
      </div>
    </div>
  );
};

export default Home;