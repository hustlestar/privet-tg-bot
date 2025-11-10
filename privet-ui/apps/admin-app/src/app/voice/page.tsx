"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from "@privet-ui/shared";
import { Mic, Volume2, Upload, Play, Pause, Download, RefreshCw, Waveform, Settings } from "lucide-react";
import { useAdminApi } from "@/hooks/useApi";
import { format } from "date-fns";

export default function VoicePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [transcriptionResult, setTranscriptionResult] = useState<any>(null);
  const [synthesisResult, setSynthesisResult] = useState<any>(null);

  const { useTranscribeAudio, useSynthesizeSpeech } = useAdminApi();
  const transcribe = useTranscribeAudio();
  const synthesize = useSynthesizeSpeech();

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
    }
  };

  const handleTranscribe = async () => {
    if (!selectedFile) return;
    
    try {
      const result = await transcribe.mutateAsync({
        audio: selectedFile,
        language: "en"
      });
      setTranscriptionResult(result);
    } catch (error) {
      console.error("Transcription failed:", error);
    }
  };

  const handleSynthesize = async (text: string) => {
    if (!text.trim()) return;
    
    try {
      const result = await synthesize.mutateAsync({
        text,
        voice_id: "default",
        language: "en"
      });
      setSynthesisResult(result);
    } catch (error) {
      console.error("Synthesis failed:", error);
    }
  };

  const voiceStats = {
    totalTranscriptions: 152,
    totalSynthesis: 89,
    successRate: 98.5,
    avgProcessingTime: 2.3,
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Mic className="w-8 h-8" />
              Voice Processing
            </h1>
            <p className="text-muted-foreground">
              Manage speech-to-text and text-to-speech operations
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-4"
      >
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Transcriptions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{voiceStats.totalTranscriptions}</div>
            <p className="text-xs text-muted-foreground">Total processed</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Synthesis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{voiceStats.totalSynthesis}</div>
            <p className="text-xs text-muted-foreground">Audio generated</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">{voiceStats.successRate}%</div>
            <p className="text-xs text-muted-foreground">Processing success</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Avg Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-info">{voiceStats.avgProcessingTime}s</div>
            <p className="text-xs text-muted-foreground">Processing time</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid gap-6 lg:grid-cols-2"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="w-5 h-5" />
              Speech-to-Text
            </CardTitle>
            <CardDescription>
              Upload audio files for transcription
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="hidden"
                id="audio-upload"
              />
              <label
                htmlFor="audio-upload"
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <Upload className="w-8 h-8 text-muted-foreground" />
                <span className="text-sm font-medium">
                  {selectedFile ? selectedFile.name : "Click to upload audio file"}
                </span>
                <span className="text-xs text-muted-foreground">
                  Supports MP3, WAV, M4A, FLAC
                </span>
              </label>
            </div>

            {audioUrl && (
              <div className="space-y-3">
                <audio controls className="w-full">
                  <source src={audioUrl} />
                  Your browser does not support the audio element.
                </audio>
                
                <div className="flex gap-2">
                  <Button 
                    onClick={handleTranscribe}
                    disabled={!selectedFile || transcribe.isPending}
                    className="flex-1"
                  >
                    {transcribe.isPending ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                        Transcribing...
                      </>
                    ) : (
                      <>
                        <Waveform className="w-4 h-4 mr-2" />
                        Transcribe
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}

            {transcriptionResult && (
              <div className="space-y-3">
                <h4 className="font-medium">Transcription Result:</h4>
                <div className="bg-muted p-3 rounded-lg">
                  <p className="text-sm">{transcriptionResult.text}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
                  <div>
                    <span className="font-medium">Language:</span> {transcriptionResult.language}
                  </div>
                  <div>
                    <span className="font-medium">Confidence:</span> {transcriptionResult.confidence}%
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Volume2 className="w-5 h-5" />
              Text-to-Speech
            </CardTitle>
            <CardDescription>
              Generate speech from text
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <textarea
                placeholder="Enter text to synthesize..."
                className="w-full h-32 px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                id="synthesis-text"
              />
              
              <div className="grid grid-cols-2 gap-3">
                <select className="px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="ru">Russian</option>
                </select>
                
                <select className="px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="default">Default Voice</option>
                  <option value="female">Female Voice</option>
                  <option value="male">Male Voice</option>
                </select>
              </div>

              <Button 
                onClick={() => {
                  const textarea = document.getElementById('synthesis-text') as HTMLTextAreaElement;
                  handleSynthesize(textarea.value);
                }}
                disabled={synthesize.isPending}
                className="w-full"
              >
                {synthesize.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Volume2 className="w-4 h-4 mr-2" />
                    Generate Speech
                  </>
                )}
              </Button>
            </div>

            {synthesisResult && (
              <div className="space-y-3">
                <h4 className="font-medium">Generated Audio:</h4>
                <audio controls className="w-full">
                  <source src={synthesisResult.audio_url} />
                  Your browser does not support the audio element.
                </audio>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Play className="w-4 h-4 mr-2" />
                    Play
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Voice Processing History</CardTitle>
            <CardDescription>Recent speech operations and their status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  id: 1,
                  type: "transcription",
                  status: "completed",
                  duration: "2.3s",
                  text: "Hello, this is a test transcription...",
                  timestamp: new Date(),
                },
                {
                  id: 2,
                  type: "synthesis",
                  status: "completed",
                  duration: "1.8s",
                  text: "Generated speech for user message",
                  timestamp: new Date(Date.now() - 300000),
                },
                {
                  id: 3,
                  type: "transcription",
                  status: "processing",
                  duration: "—",
                  text: "Processing audio file...",
                  timestamp: new Date(Date.now() - 600000),
                },
              ].map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      item.type === "transcription" ? "bg-primary" : "bg-secondary"
                    }`} />
                    <div>
                      <div className="flex items-center gap-2">
                        {item.type === "transcription" ? (
                          <Mic className="w-4 h-4" />
                        ) : (
                          <Volume2 className="w-4 h-4" />
                        )}
                        <span className="font-medium capitalize">{item.type}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          item.status === "completed" 
                            ? "bg-success/10 text-success" 
                            : "bg-warning/10 text-warning"
                        }`}>
                          {item.status}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground truncate max-w-md">
                        {item.text}
                      </p>
                    </div>
                  </div>
                  <div className="text-right text-sm text-muted-foreground">
                    <div>{item.duration}</div>
                    <div>{format(item.timestamp, "HH:mm")}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}