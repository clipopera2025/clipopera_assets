import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AudioLines, Download } from "lucide-react";

export default function ClipOperaVideoPreview() {
  return (
    <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card className="rounded-2xl shadow-lg">
        <CardContent className="space-y-4 p-4">
          <h2 className="text-xl font-bold">🎬 ClipOpera Cinematic Video</h2>
          <img src="/ClipOpera_Tee_Vertical_1080x1920.png" alt="ClipOpera Vertical Mockup" className="rounded-xl" />
          <p className="text-sm text-muted-foreground">
            A glowing black queen stands defiant in a rain-slick neon alley, wearing an oversized C L I P O P E R A tee. Thunder cracks. Neon flickers. The ground reflects her power.
          </p>
          <div className="flex items-center gap-2">
            <AudioLines className="w-4 h-4 text-primary" />
            <span className="text-xs font-medium">Trap × Cyberpunk soundtrack</span>
          </div>
          <audio controls src="/ClipOpera_Trap_Cyberpunk_Score.mp3" className="w-full" />
          <Button variant="outline" className="w-full">
            <Download className="mr-2 h-4 w-4" /> Download Assets
          </Button>
        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow-lg">
        <CardContent className="space-y-4 p-4">
          <h2 className="text-xl font-bold">🧠 Voiceover & Motion Guide</h2>
          <p className="text-sm">“This isn’t just a shirt. It’s armor for the chosen.”</p>
          <ul className="text-sm list-disc pl-4">
            <li>Install Pixflow AI Voiceover Plugin</li>
            <li>Apply Audio Spectrum & Glow FX</li>
            <li>Use Polar Coordinates for circular energy</li>
            <li>Render in H.264 with synced audio</li>
          </ul>
          <p className="text-xs text-muted-foreground">Tagline: WEAR THE STORY. FRAME THE STYLE.</p>
        </CardContent>
      </Card>
    </div>
  );
}
