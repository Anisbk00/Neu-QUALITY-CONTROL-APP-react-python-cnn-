/**
 * Viewer3D.tsx
 * 3D Model Viewer with automatic multi-view capture for NEU Surface Defect Detection
 */

import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import type { CameraView } from '../types';

interface Viewer3DProps {
  file: File | null;
  onViewsCapture: (images: string[]) => void; // sanitized base64 (no prefix)
}

interface ModelProps {
  file: File;
}

/**
 * Loads and centers a 3D model
 */
const Model: React.FC<ModelProps> = ({ file }) => {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);

  useEffect(() => {
    let revoked = false;

    const loadModel = async () => {
      const url = URL.createObjectURL(file);
      const ext = file.name.split('.').pop()?.toLowerCase();
      let loadedGeometry: THREE.BufferGeometry | null = null;

      try {
        if (ext === 'stl') {
          const loader = new STLLoader();
          loadedGeometry = await new Promise<THREE.BufferGeometry>((resolve, reject) => {
            loader.load(url, resolve, undefined, reject);
          });
        } else if (ext === 'obj') {
          const loader = new OBJLoader();
          const obj = await new Promise<THREE.Group>((resolve, reject) => {
            loader.load(url, resolve, undefined, reject);
          });
          obj.traverse((child) => {
            if ((child as any).isMesh && !loadedGeometry) {
              loadedGeometry = (child as THREE.Mesh).geometry;
            }
          });
        } else if (ext === 'gltf' || ext === 'glb') {
          const loader = new GLTFLoader();
          const gltf = await new Promise<any>((resolve, reject) => {
            loader.load(url, resolve, undefined, reject);
          });
          gltf.scene.traverse((child: any) => {
            if (child.isMesh && !loadedGeometry) {
              loadedGeometry = child.geometry;
            }
          });
        }

        if (loadedGeometry && !revoked) {
          loadedGeometry.computeBoundingBox();
          const center = new THREE.Vector3();
          loadedGeometry.boundingBox?.getCenter(center);
          loadedGeometry.translate(-center.x, -center.y, -center.z);
          setGeometry(loadedGeometry);
        }
      } catch (err) {
        console.error('Error loading model:', err);
      } finally {
        URL.revokeObjectURL(url);
      }
    };

    if (file) loadModel();

    return () => {
      revoked = true;
    };
  }, [file]);

  if (!geometry) return null;

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial color="#999999" metalness={0.3} roughness={0.7} />
    </mesh>
  );
};

/**
 * Switches camera position based on selected view
 */
const CameraController: React.FC<{ view: CameraView; onReset: () => void }> = ({ view }) => {
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  useEffect(() => {
    const distance = 50;
    switch (view) {
      case 'iso':
        camera.position.set(distance, distance, distance);
        break;
      case 'front':
        camera.position.set(0, 0, distance);
        break;
      case 'left':
        camera.position.set(-distance, 0, 0);
        break;
      case 'right':
        camera.position.set(distance, 0, 0);
        break;
      case 'top':
        camera.position.set(0, distance, 0);
        break;
    }
    camera.lookAt(0, 0, 0);
    controlsRef.current?.update();
  }, [view, camera]);

  return <OrbitControls ref={controlsRef} />;
};

/**
 * Main 3D Viewer Component
 */
const Viewer3D: React.FC<Viewer3DProps> = ({ file, onViewsCapture }) => {
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const [currentView, setCurrentView] = useState<CameraView>('iso');
  const [isCapturing, setIsCapturing] = useState(false);
  const [progress, setProgress] = useState({ index: 0, total: 0 });

  const waitFrame = (ms = 0) =>
    new Promise<void>((resolve) => requestAnimationFrame(() => (ms ? setTimeout(resolve, ms) : resolve())));

  const findCanvas = (): HTMLCanvasElement | null => {
    return wrapperRef.current?.querySelector('canvas') || null;
  };

  /**
   * Capture all predefined views in 200x200 grayscale
   */
  const captureAllViews = async () => {
    if (!wrapperRef.current) return;
    setIsCapturing(true);

    const views: CameraView[] = ['iso', 'front', 'left', 'right', 'top'];
    const targetSize = 200;
    const captures: string[] = [];

    setProgress({ index: 0, total: views.length });

    for (let i = 0; i < views.length; i++) {
      const view = views[i];
      setCurrentView(view);

      await waitFrame(50);
      await waitFrame(200);

      const canvas = findCanvas();
      if (!canvas || canvas.width === 0 || canvas.height === 0) {
        console.warn(`View ${view}: canvas invalid`);
        setProgress({ index: i + 1, total: views.length });
        continue;
      }

      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = targetSize;
      tempCanvas.height = targetSize;
      const ctx = tempCanvas.getContext('2d');
      if (!ctx) continue;

      try {
        ctx.drawImage(canvas, 0, 0, targetSize, targetSize);

        // Grayscale
        const imageData = ctx.getImageData(0, 0, targetSize, targetSize);
        const data = imageData.data;
        for (let p = 0; p < data.length; p += 4) {
          const gray = 0.299 * data[p] + 0.587 * data[p + 1] + 0.114 * data[p + 2];
          data[p] = data[p + 1] = data[p + 2] = gray;
        }
        ctx.putImageData(imageData, 0, 0);

        const dataURL = tempCanvas.toDataURL('image/png');
        const sanitized = dataURL.includes(',') ? dataURL.split(',')[1] : dataURL;

        if (sanitized.length >= 100) captures.push(sanitized);
      } catch (err) {
        console.warn(`View ${view} capture failed`, err);
      }

      setProgress({ index: i + 1, total: views.length });
    }

    setIsCapturing(false);
    setCurrentView('iso');

    if (captures.length > 0) onViewsCapture(captures);
    else console.error('No valid captures produced');
  };

  return (
    <div className="viewer-container">
      <div className="canvas-wrapper" ref={wrapperRef} style={{ width: '100%', height: '100%' }}>
        <Canvas>
          <PerspectiveCamera makeDefault position={[5, 5, 5]} />
          <CameraController view={currentView} onReset={() => setCurrentView('iso')} />
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <directionalLight position={[-10, -10, -5]} intensity={0.5} />
          {file && <Model file={file} />}
          <gridHelper args={[10, 10]} />
        </Canvas>

        {isCapturing && (
          <div
            className="capture-overlay"
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              pointerEvents: 'none',
            }}
          >
            <div
              className="capture-message"
              style={{ background: 'rgba(0,0,0,0.6)', color: '#fff', padding: '8px 12px', borderRadius: 6 }}
            >
              Capture en cours... ({progress.index}/{progress.total}) — {currentView}
            </div>
          </div>
        )}
      </div>

      <div className="viewer-controls" style={{ marginTop: 8, display: 'flex', gap: 8 }}>
        {['iso', 'front', 'left', 'right', 'top'].map((v) => (
          <button key={v} onClick={() => setCurrentView(v as CameraView)} disabled={isCapturing}>
            {`Vue ${v}`}
          </button>
        ))}
        <button onClick={() => setCurrentView('iso')} disabled={isCapturing}>
          Réinitialiser
        </button>
      </div>

      <div className="analyze-section" style={{ marginTop: 8 }}>
        <button className="analyze-button" onClick={captureAllViews} disabled={!file || isCapturing}>
          {isCapturing ? `Analyse en cours... (${progress.index}/${progress.total})` : '🔍 Analyser automatiquement'}
        </button>
      </div>
    </div>
  );
};

export default Viewer3D;
