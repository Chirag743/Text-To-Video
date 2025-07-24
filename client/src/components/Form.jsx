import React, { useState } from 'react'
import axios from 'axios'

const Form = () => {
    const [projectName, setProjectName] = useState("");
    const [topic, setTopic] = useState("");
    const [script, setScript] = useState("");
    const [scriptOption, setScriptOption] = useState("manual");
    const [isScriptLoading, setIsScriptLoading] = useState(false);
    const [isVideoLoading, setIsVideoLoading] = useState(false);
    const [videoPath, setVideoPath] = useState("");

    const handleGenerateScript = () => {
        if (topic.trim() === "") {
            alert("Please enter a topic.");
            return;
        }
        setIsScriptLoading(true);
        setScript(""); // Clear previous script
        axios.post("http://localhost:8000/generate-script", { topic }).then((response) => {
            setScript(response.data.script);
        }).catch((error) => {
            console.error("There was an error making the request:", error);
        }).finally(() => {
            setIsScriptLoading(false);
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = {
            projectName,
            topic,
            script
        };
        setIsVideoLoading(true);
        axios.post("http://localhost:8000/generate-video", formData).then((response) => {
            setVideoPath(response.data.video_path);
            alert("Video generated successfully!");
        }).catch((error) => {
            console.error("There was an error making the request:", error);
        }).finally(() => {
            setIsVideoLoading(false);
        });
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-purple-200 py-8">
            <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-xl">
                <h2 className="text-3xl font-bold text-blue-700 mb-2 text-center">Create Your Video</h2>
                <p className="text-gray-500 mb-6 text-center">Turn your ideas into engaging videos in seconds!</p>
                <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
                    <div>
                        <label className="block mb-1 text-sm font-semibold text-gray-700">Project Name</label>
                        <input
                            type="text"
                            className="border border-gray-300 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
                            placeholder="Enter project name"
                            name="projectName"
                            required
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block mb-1 text-sm font-semibold text-gray-700">Topic</label>
                        <input
                            type="text"
                            className="border border-gray-300 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
                            placeholder="Enter topic (e.g. The Water Cycle)"
                            name="topic"
                            required
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block mb-2 text-sm font-semibold text-gray-700">Script Options</label>
                        <div className="flex gap-6 justify-center">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="scriptOption"
                                    value="manual"
                                    checked={scriptOption === "manual"}
                                    onChange={() => setScriptOption("manual")}
                                    className="accent-blue-600"
                                />
                                <span>Enter your own script</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="scriptOption"
                                    value="generate"
                                    checked={scriptOption === "generate"}
                                    onChange={() => setScriptOption("generate")}
                                    className="accent-blue-600"
                                />
                                <span>Generate script from topic</span>
                            </label>
                        </div>
                    </div>
                    {scriptOption === "manual" && (
                        <div>
                            <label className="block mb-1 text-sm font-semibold text-gray-700">Script</label>
                            <textarea
                                className="border border-gray-300 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
                                placeholder="Enter your script here..."
                                name="script"
                                rows={5}
                                required
                                value={script}
                                onChange={(e) => setScript(e.target.value)}
                            />
                        </div>
                    )}
                    {scriptOption === "generate" && (
                        <div>
                            <label className="block mb-1 text-sm font-semibold text-gray-700">Script</label>
                            {script.trim() === "" ? (
                                <div className="flex flex-col items-center gap-2">
                                    <span className="text-green-700 text-sm">Script will be generated from topic.</span>
                                    <button
                                        type="button"
                                        className="bg-green-600 text-white rounded-lg px-6 py-2 font-semibold hover:bg-green-700 transition"
                                        onClick={handleGenerateScript}
                                        disabled={isScriptLoading}
                                    >
                                        {isScriptLoading ? "Generating..." : "Generate Script"}
                                    </button>
                                </div>
                            ) : (
                                <div className="bg-gray-100 rounded-lg p-4 text-gray-800 whitespace-pre-line min-h-[80px]">
                                    {script}
                                </div>
                            )}
                        </div>
                    )}
                    <button
                        type="submit"
                        className="bg-blue-600 text-white rounded-lg px-8 py-3 font-semibold text-lg hover:bg-blue-700 transition mt-2"
                        disabled={isVideoLoading}
                    >
                        {isVideoLoading ? "Generating Video..." : "Generate Video"}
                    </button>
                </form>
                {videoPath && (
                    <div className="mt-8">
                        <h3 className="text-xl font-semibold text-center mb-4 text-blue-700">Your Generated Video</h3>
                        <video
                            src={`http://localhost:8000${videoPath}`}
                            controls
                            className="w-full h-[340px] rounded-lg shadow-lg bg-black"
                        />
                        <a
                            href={`http://localhost:8000${videoPath}`}
                            download
                            className="block text-center mt-4 text-blue-600 hover:underline"
                        >
                            Download Video
                        </a>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Form