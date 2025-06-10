import React, { useRef, useState, useEffect, Suspense } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls, Stage, Html } from "@react-three/drei";
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { AudioLines, Loader2 } from "lucide-react";
import jwtDecode from "jwt-decode";

function GLTFModel({ url }) {
  const gltf = useLoader(GLTFLoader, url);
  return <primitive object={gltf.scene} scale={0.8} position={[0, -1.5, 0]} rotation={[0, Math.PI, 0]} />;
}

export default function App() {
  const [scriptPrompt, setScriptPrompt] = useState("");
  const [moodMusic, setMoodMusic] = useState("");
  const [generatedAdStatus, setGeneratedAdStatus] = useState(null);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [adResult, setAdResult] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);
  const [userToken, setUserToken] = useState(localStorage.getItem("user_token") || "");
  const [previewModel, setPreviewModel] = useState(null);
  const [userModels, setUserModels] = useState([]);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [logoutTimer, setLogoutTimer] = useState(null);
  const [lastActivity, setLastActivity] = useState(Date.now());

  const BACKEND_API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000";
  const audioRef = useRef(new Audio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'));
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleLogin = async () => {
    try {
      const response = await fetch(`${BACKEND_API_URL}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          username: loginUsername,
          password: loginPassword,
        }),
      });
      if (!response.ok) throw new Error("Login failed");
      const data = await response.json();
      localStorage.setItem("user_token", data.access_token);
      setUserToken(data.access_token);
      const decoded = jwtDecode(data.access_token);
      const expiryTime = decoded.exp * 1000;
      const currentTime = Date.now();
      const timeout = expiryTime - currentTime;
      const timer = setTimeout(() => handleLogout(), timeout);
      setLogoutTimer(timer);
      fetchUserModels();
    } catch (error) {
      alert("Login failed: " + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user_token");
    setUserToken("");
    setModelUrl(null);
    setUserModels([]);
    if (logoutTimer) clearTimeout(logoutTimer);
  };

  const handleModelUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("file", file);
      try {
        setGeneratedAdStatus("Uploading model...");
        const response = await fetch(`${BACKEND_API_URL}/upload-model`, {
          method: "POST",
          headers: userToken ? { "Authorization": `Bearer ${userToken}` } : {},
          body: formData,
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }
        const data = await response.json();
        setModelUrl(data.url);
        setGeneratedAdStatus("Model uploaded and loaded successfully.");
        fetchUserModels();
      } catch (error) {
        console.error("Error uploading model:", error);
        setGeneratedAdStatus(`Model upload failed: ${error.message}`);
      }
    }
  };

  const fetchUserModels = async () => {
    if (!userToken) return;
    try {
      const response = await fetch(`${BACKEND_API_URL}/models`, {
        headers: { "Authorization": `Bearer ${userToken}` },
      });
      if (!response.ok) {
        throw new Error("Failed to fetch models");
      }
      const data = await response.json();
      setUserModels(data);
    } catch (error) {
      console.error("Error fetching models:", error);
    }
  };

  useEffect(() => {
    fetchUserModels();
  }, [userToken]);

  useEffect(() => {
    const audio = audioRef.current;
    audio.volume = 0.5;
    audio.loop = true;
    return () => {
      audio.pause();
      audio.src = '';
    };
  }, []);

  useEffect(() => {
    const resetActivity = () => setLastActivity(Date.now());
    const checkInactivity = setInterval(() => {
      if (Date.now() - lastActivity > 15 * 60 * 1000) handleLogout();
    }, 60 * 1000);

    window.addEventListener("mousemove", resetActivity);
    window.addEventListener("keydown", resetActivity);

    return () => {
      clearInterval(checkInactivity);
      window.removeEventListener("mousemove", resetActivity);
      window.removeEventListener("keydown", resetActivity);
    };
  }, [lastActivity]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8 font-inter text-white relative">
      {!userToken && (
        <div className="absolute top-4 left-4 bg-gray-700 p-4 rounded-lg shadow-lg">
          <input
            type="text"
            placeholder="Username"
            value={loginUsername}
            onChange={(e) => setLoginUsername(e.target.value)}
            className="mb-2 p-2 w-full rounded bg-gray-800 text-white"
          />
          <input
            type="password"
            placeholder="Password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            className="mb-2 p-2 w-full rounded bg-gray-800 text-white"
          />
          <Button onClick={handleLogin} className="w-full bg-blue-600 hover:bg-blue-700">Login</Button>
        </div>
      )}

      {userToken && (
        <Button onClick={handleLogout} className="absolute top-4 left-4 bg-red-600 hover:bg-red-700">Logout</Button>
      )}

      <button onClick={togglePlay} className="absolute top-8 right-8 z-50 p-4 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-xl">
        <AudioLines className={`w-7 h-7 ${isPlaying ? 'text-green-300 animate-pulse' : 'text-white'}`} />
      </button>

      <h1 className="text-5xl font-extrabold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
        ClipOpera AI Ad Studio
      </h1>

      {userToken && (
        <div className="mb-8 text-center">
          <input type="file" accept=".glb,.gltf,.zip,.fbx,.obj" onChange={handleModelUpload} className="mb-4" />
          {generatedAdStatus && <p className="text-sm text-gray-400">{generatedAdStatus}</p>}
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {userModels.map((model) => (
              <Card key={model.id} className="w-48 cursor-pointer hover:shadow-lg" onClick={() => setModelUrl(model.url)}>
                <CardContent className="p-2 text-sm text-center truncate">{model.name}</CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      <div className="h-[600px] rounded-xl overflow-hidden">
        <Canvas camera={{ position: [0, 0, 5] }} shadows>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <Suspense fallback={<Html center><Loader2 className="animate-spin" /></Html>}>
            <OrbitControls enableZoom />
            <Stage>
              {modelUrl ? <GLTFModel url={modelUrl} /> : <mesh><boxGeometry /><meshStandardMaterial color="gray" /></mesh>}
            </Stage>
          </Suspense>
        </Canvas>
      </div>
    </div>
  );
}
