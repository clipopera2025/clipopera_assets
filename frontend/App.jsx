// Demo React frontend for interacting with the ClipOpera API
import React, { useRef, useState, useEffect, Suspense } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls, Stage, Html } from "@react-three/drei";
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { Card, CardContent } from "./components/ui/card";
import Button from "./components/ui/button";
import { AudioLines, Loader2, Link, LogIn, UserPlus, Sparkle, Wand2, Video, Lightbulb } from "lucide-react";
import jwtDecode from "jwt-decode";

// Define your video templates here, before the App component
const VIDEO_TEMPLATES = [
  { id: 'standard', name: 'Standard Ad' },
  { id: 'fast_paced', name: 'Fast Paced' },
  { id: 'luxury_showcase', name: 'Luxury Showcase' },
  { id: 'explainer', name: 'Explainer Video' },
  { id: 'anime_10s', name: 'Anime Cartoon (10s)' },
  { id: 'anime_30s', name: 'Anime Cartoon (30s)' },
  { id: 'anime_60s', name: 'Anime Cartoon (60s)' },
];

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
  const [registerUsername, setRegisterUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [logoutTimer, setLogoutTimer] = useState(null);
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [showTimeoutWarning, setShowTimeoutWarning] = useState(false);
  const [metaAccountLinked, setMetaAccountLinked] = useState(false);
  const timeoutWarningRef = useRef(null);
  const [metaTokenExpiry, setMetaTokenExpiry] = useState(null);
  const [audioOverviewUrl, setAudioOverviewUrl] = useState(null);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(VIDEO_TEMPLATES[0].id);
  const [viralScore, setViralScore] = useState(null);
  const [toneAnalysis, setToneAnalysis] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState(null);
  const [suggestedPrompts, setSuggestedPrompts] = useState([]);

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

  const checkMetaAccountStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_API_URL}/meta-status`, {
        headers: { Authorization: `Bearer ${userToken}` },
      });
      const data = await response.json();
      setMetaAccountLinked(data.linked === true);
    } catch (error) {
      console.error("Error checking Meta account status:", error);
    }
  };

  const startMetaOAuth = () => {
    window.location.href = `${BACKEND_API_URL}/api/v1/platforms/meta/auth_start`;
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
      if (timeoutWarningRef.current) clearTimeout(timeoutWarningRef.current);
      timeoutWarningRef.current = setTimeout(() => setShowTimeoutWarning(true), timeout - 2 * 60 * 1000);
      const timer = setTimeout(() => handleLogout(), timeout);
      setLogoutTimer(timer);
      fetchUserModels();
      checkMetaAccountStatus();
    } catch (error) {
      alert("Login failed: " + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user_token");
    setUserToken("");
    setModelUrl(null);
    setUserModels([]);
    setShowTimeoutWarning(false);
    if (logoutTimer) clearTimeout(logoutTimer);
    if (timeoutWarningRef.current) clearTimeout(timeoutWarningRef.current);
  };

  const handleRegister = async () => {
    try {
      const response = await fetch(`${BACKEND_API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: registerUsername, password: registerPassword }),
      });
      if (!response.ok) throw new Error("Registration failed");
      alert("Registration successful! Please log in.");
    } catch (error) {
      alert("Registration error: " + error.message);
    }
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
      {showTimeoutWarning && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-70">
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg text-center animate-pulse">
            <h2 className="text-lg font-bold mb-2 text-yellow-400">Session Expiring Soon</h2>
            <p className="mb-4">You will be logged out in less than 2 minutes due to inactivity.</p>
            <Button onClick={() => {
              setShowTimeoutWarning(false);
              setLastActivity(Date.now());
              handleLogin();
            }}>Stay Logged In</Button>
          </div>
        </div>
      )}

      <button onClick={togglePlay} className="absolute top-8 right-8 z-50 p-4 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-xl">
        <AudioLines className={`w-7 h-7 ${isPlaying ? 'text-green-300 animate-pulse' : 'text-white'}`} />
      </button>

      <h1 className="text-5xl font-extrabold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
        ClipOpera AI Ad Studio
      </h1>

      {!userToken && (
        <div className="mb-8 text-center space-y-4">
          <div className="flex flex-col items-center gap-2">
            <input type="text" placeholder="Username" value={loginUsername} onChange={(e) => setLoginUsername(e.target.value)} className="p-2 rounded bg-gray-800 text-white" />
            <input type="password" placeholder="Password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} className="p-2 rounded bg-gray-800 text-white" />
            <Button onClick={handleLogin} className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2"><LogIn size={16}/>Login</Button>
          </div>
          <div className="flex flex-col items-center gap-2 border-t border-gray-700 pt-4">
            <input type="text" placeholder="New Username" value={registerUsername} onChange={(e) => setRegisterUsername(e.target.value)} className="p-2 rounded bg-gray-800 text-white" />
            <input type="password" placeholder="New Password" value={registerPassword} onChange={(e) => setRegisterPassword(e.target.value)} className="p-2 rounded bg-gray-800 text-white" />
            <Button onClick={handleRegister} className="bg-green-600 hover:bg-green-700 flex items-center gap-2"><UserPlus size={16}/>Register</Button>
          </div>
        </div>
      )}

      {userToken && (
        <div className="absolute top-4 left-4 flex gap-2">
          <Button onClick={handleLogout} className="bg-red-600 hover:bg-red-700">Logout</Button>
          <Button onClick={startMetaOAuth} disabled={metaAccountLinked} className="bg-purple-600 hover:bg-purple-700 flex items-center gap-2">
            <Link size={16}/>{metaAccountLinked ? 'Meta Linked' : 'Link Meta'}
          </Button>
        </div>
      )}

      {userToken && (
        <div className="mb-8 text-center">
          <input type="file" accept=".glb,.gltf,.zip,.fbx,.obj" onChange={handleModelUpload} className="mb-4" />
          {generatedAdStatus && <p className="text-sm text-gray-400">{generatedAdStatus}</p>}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mt-4">
            {userModels.map((model) => (
              <Card key={model.id} className="bg-gray-900 border border-gray-700 hover:shadow-xl hover:border-purple-500 transition-all duration-300 cursor-pointer" onClick={() => setModelUrl(model.url)}>
                <CardContent className="p-2 text-center truncate">
                  <span className="block text-white font-semibold text-sm">{model.name}</span>
                  <span className="text-xs text-purple-400">{new URL(model.url).hostname}</span>
                </CardContent>
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
