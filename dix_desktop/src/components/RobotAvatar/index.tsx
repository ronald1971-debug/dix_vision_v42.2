// Robot Avatar Component - Exports the simple 3D robot

import { createSimpleRobot, animateRobot, setTalking, setExpression, setChestButtonColor } from './simpleRobot';
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { exit as tauriExit } from '@tauri-apps/plugin-process';

interface RobotAvatarProps {
    width: number;
    height: number;
    isSpeaking?: boolean;
    expression?: string;
    speechText?: string | null;
}

export default function RobotAvatar({ width, height, isSpeaking = false, expression = 'neutral', speechText = null }: RobotAvatarProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const robotRef = useRef<THREE.Group | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const animationIdRef = useRef<number | undefined>(undefined);
    const raycasterRef = useRef<THREE.Raycaster>(new THREE.Raycaster());
    const mouseRef = useRef<THREE.Vector2>(new THREE.Vector2());

    useEffect(() => {
        if (!containerRef.current) return;

        // Scene setup
        const scene = new THREE.Scene();
        // Transparent background for DIX DESKTOP

        // Camera
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.z = 4;
        camera.position.y = 0.5;

        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);
        containerRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        scene.add(directionalLight);

        const blueLight = new THREE.PointLight(0x00BFFF, 0.8, 10);
        blueLight.position.set(2, 2, 3);
        scene.add(blueLight);

        // Create robot
        const robot = createSimpleRobot();
        scene.add(robot);
        robotRef.current = robot;

        // Handle clicks
        const handleClick = (event: MouseEvent) => {
            if (!containerRef.current || !robotRef.current) return;

            const rect = containerRef.current.getBoundingClientRect();
            const mouse = mouseRef.current;
            const raycaster = raycasterRef.current;

            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(robotRef.current.children, true);

            for (const intersect of intersects) {
                if (intersect.object.name === 'chestLight') {
                    // Turn chest button red and close app
                    setChestButtonColor(true, robotRef.current);
                    setTimeout(() => {
                        tauriExit(0);
                    }, 500); // Small delay to show red color
                    break;
                }
            }
        };

        // Handle right-click as alternative close
        const handleRightClick = (event: MouseEvent) => {
            event.preventDefault();
            tauriExit(0);
        };

        // Handle keyboard shortcut for closing
        const handleKeyDown = (event: KeyboardEvent) => {
            // ESC or Ctrl+Q to close
            if (event.key === 'Escape' || (event.ctrlKey && event.key === 'q')) {
                tauriExit(0);
            }
        };

        // Handle hover to show cursor change
        const handleMouseMove = (event: MouseEvent) => {
            if (!containerRef.current || !robotRef.current) return;

            const rect = containerRef.current.getBoundingClientRect();
            const mouse = mouseRef.current;
            const raycaster = raycasterRef.current;

            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(robotRef.current.children, true);

            let onChestButton = false;
            for (const intersect of intersects) {
                if (intersect.object.name === 'chestLight') {
                    onChestButton = true;
                    break;
                }
            }
            
            containerRef.current.style.cursor = onChestButton ? 'pointer' : 'default';
        };

        containerRef.current.addEventListener('click', handleClick);
        containerRef.current.addEventListener('mousemove', handleMouseMove);
        containerRef.current.addEventListener('contextmenu', handleRightClick);
        window.addEventListener('keydown', handleKeyDown);

        // Animation loop
        const animate = (time: number) => {
            const timeSeconds = time / 1000;
            
            // Update talking state
            setTalking(isSpeaking);
            
            // Update expression
            setExpression(expression);
            
            // Animate robot
            if (robotRef.current) {
                animateRobot(robotRef.current, timeSeconds);
            }

            renderer.render(scene, camera);
            animationIdRef.current = requestAnimationFrame(animate);
        };

        animate(0);

        // Cleanup
        return () => {
            if (animationIdRef.current) {
                cancelAnimationFrame(animationIdRef.current);
            }
            if (renderer.domElement && containerRef.current) {
                containerRef.current.removeEventListener('click', handleClick);
                containerRef.current.removeEventListener('mousemove', handleMouseMove);
                containerRef.current.removeEventListener('contextmenu', handleRightClick);
                containerRef.current.removeChild(renderer.domElement);
            }
            window.removeEventListener('keydown', handleKeyDown);
            renderer.dispose();
        };
    }, [width, height, isSpeaking, expression, speechText]);

    return (
        <div
            ref={containerRef}
            style={{
                width,
                height,
                position: 'absolute',
                left: '50%',
                bottom: 0,
                transform: 'translateX(-50%)',
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'center',
                cursor: 'default',
            }}
        >
            {speechText && (
                <div
                    style={{
                        position: 'absolute',
                        top: '20%',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        color: 'white',
                        padding: '12px 20px',
                        borderRadius: '20px',
                        maxWidth: '80%',
                        fontSize: '14px',
                        zIndex: 100,
                        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        animation: isSpeaking ? 'pulse 1.5s infinite' : 'none',
                    }}
                >
                    {speechText}
                    <style>{`
                        @keyframes pulse {
                            0%, 100% { transform: translateX(-50%) scale(1); }
                            50% { transform: translateX(-50%) scale(1.02); }
                        }
                    `}</style>
                </div>
            )}
        </div>
    );
}
