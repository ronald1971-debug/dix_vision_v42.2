// Robot Avatar Component - Exports the simple 3D robot

import { createSimpleRobot, animateRobot } from './simpleRobot';
import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface RobotAvatarProps {
    width: number;
    height: number;
}

export default function RobotAvatar({ width, height }: RobotAvatarProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const robotRef = useRef<THREE.Group | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const animationIdRef = useRef<number | undefined>(undefined);

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

        // Animation loop
        const animate = (time: number) => {
            const timeSeconds = time / 1000;
            
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
                containerRef.current.removeChild(renderer.domElement);
            }
            renderer.dispose();
        };
    }, [width, height]);

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
            }}
        />
    );
}
