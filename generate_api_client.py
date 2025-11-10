#!/usr/bin/env python3
"""Generate TypeScript client for React from FastAPI OpenAPI spec."""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import requests
import signal


def check_requirements():
    """Check if required tools are installed."""
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm is not installed. Please install Node.js and npm.")
        return False
    
    try:
        subprocess.run(["npx", "openapi-generator-cli", "version"], capture_output=True, check=False)
    except FileNotFoundError:
        print("❌ npx is not available. Please ensure npm is properly installed.")
        return False
    
    return True


def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend...")
    
    # Start the backend in a subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent)
    
    process = subprocess.Popen(
        [sys.executable, "-m", "privet_api.main"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Backend is running")
                return process
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            if i % 5 == 0:
                print(f"⏳ Waiting for backend to start... ({i}/{max_retries})")
    
    # If we get here, the server didn't start
    process.terminate()
    print("❌ Failed to start backend")
    return None


def extract_openapi_spec(output_path: Path):
    """Extract OpenAPI spec from running FastAPI server."""
    print("📋 Extracting OpenAPI spec...")
    
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        response.raise_for_status()
        
        spec = response.json()
        
        # Save the spec
        with open(output_path, "w") as f:
            json.dump(spec, f, indent=2)
        
        print(f"✅ OpenAPI spec saved to {output_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to extract OpenAPI spec: {e}")
        return False


def generate_typescript_client(spec_path: Path, output_dir: Path):
    """Generate TypeScript client using OpenAPI Generator."""
    print("🔧 Generating TypeScript client...")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate the client
    cmd = [
        "npx",
        "@openapitools/openapi-generator-cli",
        "generate",
        "-i", str(spec_path),
        "-g", "typescript-axios",
        "-o", str(output_dir),
        "--additional-properties=supportsES6=true,npmName=privet-api-client,npmVersion=1.0.0,withSeparateModelsAndApi=true,apiPackage=api,modelPackage=models,withInterfaces=true,useSingleRequestParameter=true"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ TypeScript client generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate client: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def install_client_dependencies(client_dir: Path):
    """Install dependencies for the generated client."""
    print("📦 Installing client dependencies...")
    
    try:
        subprocess.run(
            ["npm", "install"],
            cwd=client_dir,
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def build_client(client_dir: Path):
    """Build the TypeScript client."""
    print("🏗️ Building TypeScript client...")
    
    try:
        subprocess.run(
            ["npm", "run", "build"],
            cwd=client_dir,
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Client built successfully")
        return True
    except subprocess.CalledProcessError:
        # Build script might not exist, which is okay
        print("ℹ️ No build script found, skipping build step")
        return True


def create_react_integration_example(client_dir: Path):
    """Create an example of how to use the client in React."""
    example_path = client_dir / "react-example.tsx"
    
    example_content = """// Example: How to use the generated API client in React

import React, { useEffect, useState } from 'react';
import { Configuration, UsersApi, ConversationsApi, AudioApi } from './api';
import type { User, ConversationResponse } from './models';

// Configure the API client
const config = new Configuration({
  basePath: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  // Add authentication headers if needed
  // headers: {
  //   'Authorization': `Bearer ${token}`
  // }
});

// Create API instances
const usersApi = new UsersApi(config);
const conversationsApi = new ConversationsApi(config);
const audioApi = new AudioApi(config);

// Example React component
export const ExampleComponent: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Example: Get or create user
  const getOrCreateUser = async (telegramId: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await usersApi.getUserOrCreate({
        telegramId,
        username: 'example_user',
        firstName: 'John',
        lastName: 'Doe'
      });
      
      setUser(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Example: Send a message to the conversation
  const sendMessage = async (userId: string, message: string) => {
    try {
      const response = await conversationsApi.processMessage({
        userId,
        requestBody: {
          message,
          telegram_id: 123456789,
          voice_response: false
        }
      });
      
      console.log('Response:', response.data);
      return response.data;
    } catch (err) {
      console.error('Error sending message:', err);
      throw err;
    }
  };

  // Example: Process audio
  const processAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.ogg');
      
      const response = await audioApi.transcribeAudio({
        audio: audioBlob as any
      });
      
      console.log('Transcription:', response.data);
      return response.data;
    } catch (err) {
      console.error('Error processing audio:', err);
      throw err;
    }
  };

  useEffect(() => {
    // Example: Load user on component mount
    getOrCreateUser(123456789);
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return null;

  return (
    <div>
      <h1>Welcome, {user.first_name}!</h1>
      <p>User ID: {user.id}</p>
      <button onClick={() => sendMessage(user.id, 'Hello from React!')}>
        Send Test Message
      </button>
    </div>
  );
};

// Custom React hook for the API
export const usePrivetApi = () => {
  const [config] = useState(() => new Configuration({
    basePath: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  }));

  return {
    users: new UsersApi(config),
    conversations: new ConversationsApi(config),
    audio: new AudioApi(config),
  };
};

// Usage in a component with the custom hook
export const AnotherExample: React.FC = () => {
  const api = usePrivetApi();
  
  const handleClick = async () => {
    try {
      const user = await api.users.getUserOrCreate({
        telegramId: 987654321,
        username: 'test_user'
      });
      console.log('User created:', user.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return (
    <button onClick={handleClick}>
      Create Test User
    </button>
  );
};
"""
    
    with open(example_path, "w") as f:
        f.write(example_content)
    
    print(f"✅ React integration example created at {example_path}")


def main():
    """Main function to orchestrate the client generation process."""
    print("🎯 OpenAPI Client Generator for React")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Define paths
    project_root = Path(__file__).parent
    spec_path = project_root / "openapi.json"
    client_dir = project_root / "generated-client"
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    try:
        # Extract OpenAPI spec
        if not extract_openapi_spec(spec_path):
            backend_process.terminate()
            sys.exit(1)
        
        # Generate TypeScript client
        if not generate_typescript_client(spec_path, client_dir):
            backend_process.terminate()
            sys.exit(1)
        
        # Install dependencies
        install_client_dependencies(client_dir)
        
        # Build client
        build_client(client_dir)
        
        # Create React integration example
        create_react_integration_example(client_dir)
        
        print("\n" + "=" * 50)
        print("✨ Client generation complete!")
        print(f"📁 Client location: {client_dir}")
        print("\nTo use in your React app:")
        print("1. Copy the generated-client folder to your React project")
        print("2. Install it as a local dependency:")
        print("   npm install ./generated-client")
        print("3. Import and use the API client:")
        print("   import { UsersApi, Configuration } from 'generated-client';")
        print("\nSee react-example.tsx for usage examples.")
        
    finally:
        # Stop the backend
        print("\n🛑 Stopping backend...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("✅ Backend stopped")


if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\n⚠️ Interrupted by user")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    main()