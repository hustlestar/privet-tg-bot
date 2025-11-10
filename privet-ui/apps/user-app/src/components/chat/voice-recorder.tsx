"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@privet-ui/shared";
import { Mic, MicOff, X, Send } from "lucide-react";

interface VoiceRecorderProps {
  onClose: () => void;
  onTranscript: (text: string) => void;
}

export function VoiceRecorder({ onClose, onTranscript }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>();
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Set up audio analysis for visualization
      audioContextRef.current = new AudioContext();
      analyzerRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyzerRef.current);
      analyzerRef.current.fftSize = 256;
      
      // Start recording
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks: BlobPart[] = [];
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        // Here you would send the blob to the API
        // For demo, we'll just simulate a transcript
        setTimeout(() => {
          onTranscript("This is a simulated transcript of your voice message.");
        }, 1000);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      startTimeRef.current = Date.now();
      
      // Start visualization
      visualize();
      updateDuration();
    } catch (error) {
      console.error("Failed to start recording:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };

  const visualize = () => {
    if (!analyzerRef.current) return;
    
    const dataArray = new Uint8Array(analyzerRef.current.frequencyBinCount);
    analyzerRef.current.getByteFrequencyData(dataArray);
    
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    setAudioLevel(average / 255);
    
    if (isRecording) {
      animationFrameRef.current = requestAnimationFrame(visualize);
    }
  };

  const updateDuration = () => {
    if (isRecording) {
      setDuration(Math.floor((Date.now() - startTimeRef.current) / 1000));
      setTimeout(updateDuration, 100);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <motion.div
          className="w-32 h-32 rounded-full bg-primary/20 flex items-center justify-center"
          animate={isRecording ? {
            scale: [1, 1 + audioLevel * 0.3, 1],
          } : {}}
          transition={{
            duration: 0.2,
            repeat: Infinity,
          }}
        >
          <motion.button
            className="w-24 h-24 rounded-full bg-primary text-primary-foreground flex items-center justify-center"
            onClick={isRecording ? stopRecording : startRecording}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isRecording ? (
              <MicOff className="w-10 h-10" />
            ) : (
              <Mic className="w-10 h-10" />
            )}
          </motion.button>
        </motion.div>
        
        {isRecording && (
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-primary"
            initial={{ scale: 1, opacity: 1 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
            }}
          />
        )}
      </div>

      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          {isRecording ? "Recording..." : "Tap to start recording"}
        </p>
        {isRecording && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-2xl font-mono mt-2"
          >
            {formatDuration(duration)}
          </motion.p>
        )}
      </div>

      <div className="flex gap-2">
        <Button
          onClick={onClose}
          variant="outline"
          size="sm"
        >
          <X className="w-4 h-4 mr-1" />
          Cancel
        </Button>
        {!isRecording && duration > 0 && (
          <Button
            onClick={() => {
              onClose();
            }}
            size="sm"
          >
            <Send className="w-4 h-4 mr-1" />
            Send
          </Button>
        )}
      </div>
    </div>
  );
}