// Simple 3D Robot Avatar - Code-Based Generation
// This creates a basic robot using Three.js primitives
// Sonny-inspired design from I, Robot

import * as THREE from 'three';

export interface RobotParts {
    head: THREE.Mesh;
    leftEye: THREE.Mesh;
    rightEye: THREE.Mesh;
    mouth: THREE.Mesh;
    chestLight: THREE.Mesh;
    leftEyebrow: THREE.Mesh;
    rightEyebrow: THREE.Mesh;
}

export function createSimpleRobot(): THREE.Group {
    const robot = new THREE.Group();

    // Materials - Sonny-inspired champagne/metallic colors
    const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0xE6D3A3, // Champagne gold
        metalness: 0.8,
        roughness: 0.2,
    });

    const darkMaterial = new THREE.MeshStandardMaterial({
        color: 0x8B7355, // Dark metallic
        metalness: 0.9,
        roughness: 0.1,
    });

    const eyeMaterial = new THREE.MeshStandardMaterial({
        color: 0x00BFFF, // Glowing blue (Sonny's eye color)
        emissive: 0x00BFFF,
        emissiveIntensity: 0.8,
        metalness: 0.5,
    });

    // Head
    const headGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const head = new THREE.Mesh(headGeometry, bodyMaterial);
    head.position.y = 1.7;
    head.name = 'head';
    robot.add(head);

    // Eyes (Sonny-style glowing blue)
    const eyeGeometry = new THREE.SphereGeometry(0.08, 16, 16);
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.15, 1.75, 0.4);
    leftEye.name = 'leftEye';
    robot.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.15, 1.75, 0.4);
    rightEye.name = 'rightEye';
    robot.add(rightEye);

    // Eyebrows for expressions
    const eyebrowGeometry = new THREE.BoxGeometry(0.15, 0.02, 0.02);
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, darkMaterial);
    leftEyebrow.position.set(-0.15, 1.82, 0.45);
    leftEyebrow.name = 'leftEyebrow';
    robot.add(leftEyebrow);

    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, darkMaterial);
    rightEyebrow.position.set(0.15, 1.82, 0.45);
    rightEyebrow.name = 'rightEyebrow';
    robot.add(rightEyebrow);

    // Mouth (initially closed, will animate when talking)
    const mouthGeometry = new THREE.BoxGeometry(0.12, 0.02, 0.02);
    const mouth = new THREE.Mesh(mouthGeometry, darkMaterial);
    mouth.position.set(0, 1.6, 0.45);
    mouth.name = 'mouth';
    robot.add(mouth);

    // Neck
    const neckGeometry = new THREE.CylinderGeometry(0.15, 0.2, 0.2, 16);
    const neck = new THREE.Mesh(neckGeometry, darkMaterial);
    neck.position.y = 1.4;
    robot.add(neck);

    // Torso
    const torsoGeometry = new THREE.CylinderGeometry(0.4, 0.35, 0.8, 32);
    const torso = new THREE.Mesh(torsoGeometry, bodyMaterial);
    torso.position.y = 0.9;
    robot.add(torso);

    // Chest button (Sonny feature - the "brain" indicator)
    const chestLightGeometry = new THREE.CircleGeometry(0.1, 32);
    const chestLight = new THREE.Mesh(chestLightGeometry, eyeMaterial);
    chestLight.position.set(0, 1.1, 0.4);
    chestLight.name = 'chestLight';
    robot.add(chestLight);

    // Shoulders
    const shoulderGeometry = new THREE.SphereGeometry(0.2, 16, 16);
    const leftShoulder = new THREE.Mesh(shoulderGeometry, darkMaterial);
    leftShoulder.position.set(-0.5, 1.2, 0);
    robot.add(leftShoulder);

    const rightShoulder = new THREE.Mesh(shoulderGeometry, darkMaterial);
    rightShoulder.position.set(0.5, 1.2, 0);
    robot.add(rightShoulder);

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.08, 0.1, 0.6, 16);
    const leftArm = new THREE.Mesh(armGeometry, bodyMaterial);
    leftArm.position.set(-0.65, 0.8, 0);
    leftArm.rotation.z = 0.2;
    robot.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, bodyMaterial);
    rightArm.position.set(0.65, 0.8, 0);
    rightArm.rotation.z = -0.2;
    robot.add(rightArm);

    // Hands
    const handGeometry = new THREE.SphereGeometry(0.12, 16, 16);
    const leftHand = new THREE.Mesh(handGeometry, darkMaterial);
    leftHand.position.set(-0.75, 0.45, 0);
    robot.add(leftHand);

    const rightHand = new THREE.Mesh(handGeometry, darkMaterial);
    rightHand.position.set(0.75, 0.45, 0);
    robot.add(rightHand);

    // Hips
    const hipGeometry = new THREE.SphereGeometry(0.25, 16, 16);
    const hip = new THREE.Mesh(hipGeometry, darkMaterial);
    hip.position.y = 0.4;
    robot.add(hip);

    // Legs
    const legGeometry = new THREE.CylinderGeometry(0.12, 0.1, 0.7, 16);
    const leftLeg = new THREE.Mesh(legGeometry, bodyMaterial);
    leftLeg.position.set(-0.2, 0.05, 0);
    robot.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeometry, bodyMaterial);
    rightLeg.position.set(0.2, 0.05, 0);
    robot.add(rightLeg);

    // Feet
    const footGeometry = new THREE.BoxGeometry(0.15, 0.1, 0.25);
    const leftFoot = new THREE.Mesh(footGeometry, darkMaterial);
    leftFoot.position.set(-0.2, -0.35, 0.05);
    robot.add(leftFoot);

    const rightFoot = new THREE.Mesh(footGeometry, darkMaterial);
    rightFoot.position.set(0.2, -0.35, 0.05);
    robot.add(rightFoot);

    // Store references for animation
    (robot as any).robotParts = {
        head,
        leftEye,
        rightEye,
        mouth,
        chestLight,
        leftEyebrow,
        rightEyebrow,
    } as RobotParts;

    return robot;
}

// Animation state for talking
let isTalking = false;
let talkStartTime = 0;
let expression = 'neutral'; // neutral, happy, sad, angry, surprised

export function setTalking(talking: boolean) {
    isTalking = talking;
    if (talking) {
        talkStartTime = Date.now();
    }
}

export function setExpression(newExpression: string) {
    expression = newExpression;
}

export function setChestButtonColor(red: boolean, robot: THREE.Group) {
    const parts = (robot as any).robotParts as RobotParts;
    if (parts && parts.chestLight) {
        if (red) {
            (parts.chestLight.material as THREE.MeshStandardMaterial).color.setHex(0xFF0000);
            (parts.chestLight.material as THREE.MeshStandardMaterial).emissive.setHex(0xFF0000);
        } else {
            (parts.chestLight.material as THREE.MeshStandardMaterial).color.setHex(0x00BFFF);
            (parts.chestLight.material as THREE.MeshStandardMaterial).emissive.setHex(0x00BFFF);
        }
    }
}

// Animation function for idle movement and talking
export function animateRobot(robot: THREE.Group, time: number): void {
    const parts = (robot as any).robotParts as RobotParts;
    if (!parts) return;

    // Subtle breathing (robot doesn't really breathe, but subtle movement)
    robot.position.y = Math.sin(time * 2) * 0.02;

    // Head movement (tracking/awareness)
    if (parts.head) {
        parts.head.rotation.y = Math.sin(time * 0.5) * 0.1;
        parts.head.rotation.x = Math.sin(time * 0.7) * 0.05;
    }

    // Eye glow pulsing (Sonny's eyes glow)
    [parts.leftEye, parts.rightEye].forEach(eye => {
        if (eye && eye instanceof THREE.Mesh) {
            (eye.material as THREE.MeshStandardMaterial).emissiveIntensity = 
                0.6 + Math.sin(time * 3) * 0.2;
        }
    });

    // Mouth animation when talking
    if (parts.mouth) {
        if (isTalking) {
            const talkTime = (Date.now() - talkStartTime) / 1000;
            // Open and close mouth based on sine wave
            const mouthOpen = Math.abs(Math.sin(talkTime * 10)) * 0.08;
            parts.mouth.scale.y = 1 + mouthOpen;
            parts.mouth.position.y = 1.6 - mouthOpen * 0.5;
        } else {
            // Closed mouth
            parts.mouth.scale.y = 1;
            parts.mouth.position.y = 1.6;
        }
    }

    // Facial expressions
    if (parts.leftEyebrow && parts.rightEyebrow) {
        switch (expression) {
            case 'happy':
                parts.leftEyebrow.rotation.z = -0.2;
                parts.rightEyebrow.rotation.z = 0.2;
                parts.leftEyebrow.position.y = 1.83;
                parts.rightEyebrow.position.y = 1.83;
                break;
            case 'sad':
                parts.leftEyebrow.rotation.z = 0.3;
                parts.rightEyebrow.rotation.z = -0.3;
                parts.leftEyebrow.position.y = 1.81;
                parts.rightEyebrow.position.y = 1.81;
                break;
            case 'angry':
                parts.leftEyebrow.rotation.z = 0.4;
                parts.rightEyebrow.rotation.z = -0.4;
                parts.leftEyebrow.position.y = 1.84;
                parts.rightEyebrow.position.y = 1.84;
                break;
            case 'surprised':
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.86;
                parts.rightEyebrow.position.y = 1.86;
                break;
            default: // neutral
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.82;
                parts.rightEyebrow.position.y = 1.82;
        }
    }

    // Eye shape changes based on expression
    if (parts.leftEye && parts.rightEye) {
        const eyeScaleX = expression === 'happy' ? 1.3 : 
                         expression === 'sad' ? 0.8 : 
                         expression === 'surprised' ? 1.2 : 1;
        parts.leftEye.scale.x = eyeScaleX;
        parts.rightEye.scale.x = eyeScaleX;
    }

    // Arm sway (subtle natural movement)
    const leftArm = robot.children[10];
    const rightArm = robot.children[11];
    if (leftArm && rightArm) {
        leftArm.rotation.z = 0.2 + Math.sin(time * 1) * 0.05;
        rightArm.rotation.z = -0.2 - Math.sin(time * 1) * 0.05;
    }
}
