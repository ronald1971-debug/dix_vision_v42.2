// Sonny-Inspired Robot Avatar - Build Plan Implementation
// Following DIXVISION v42.2 Architecture Requirements
// White Composite Shell, Mechanical Joints, Transparent Core, Expressive Face

import * as THREE from 'three';

export interface RobotParts {
    head: THREE.Mesh;
    leftEye: THREE.Mesh;
    rightEye: THREE.Mesh;
    mouth: THREE.Mesh;
    jaw: THREE.Mesh;
    chestLight: THREE.Mesh;
    leftEyebrow: THREE.Mesh;
    rightEyebrow: THREE.Mesh;
    leftArm: THREE.Mesh;
    rightArm: THREE.Mesh;
    leftHand: THREE.Mesh;
    rightHand: THREE.Mesh;
    torso: THREE.Mesh;
    neck: THREE.Mesh;
    core: THREE.Mesh;
}

export function createSimpleRobot(): THREE.Group {
    const robot = new THREE.Group();

    // Materials - Sonny-inspired White Composite Shell
    const shellMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFFFFF, // White composite shell
        metalness: 0.8,
        roughness: 0.2,
    });

    const jointMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a1a, // Dark mechanical joints
        metalness: 0.9,
        roughness: 0.1,
    });

    const eyeMaterial = new THREE.MeshStandardMaterial({
        color: 0x00BFFF, // Glowing blue eyes (Sonny's color)
        emissive: 0x00BFFF,
        emissiveIntensity: 0.8,
        metalness: 0.5,
    });

    const mouthMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a1a, // Dark mouth for contrast
        emissive: 0x000000,
        emissiveIntensity: 0.0,
        metalness: 0.6,
        roughness: 0.4,
    });

    const coreMaterial = new THREE.MeshStandardMaterial({
        color: 0x00BFFF, // Transparent blue core
        emissive: 0x00BFFF,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.6,
    });

    // Head - White composite shell, human proportions
    const headGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const head = new THREE.Mesh(headGeometry, shellMaterial);
    head.position.y = 1.75;
    head.name = 'head';
    robot.add(head);

    // Eyes - Sonny-style glowing blue with proper size
    const eyeGeometry = new THREE.SphereGeometry(0.08, 16, 16);
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.15, 1.8, 0.4);
    leftEye.name = 'leftEye';
    robot.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.15, 1.8, 0.4);
    rightEye.name = 'rightEye';
    robot.add(rightEye);

    // Eyebrows for expressions
    const eyebrowGeometry = new THREE.BoxGeometry(0.15, 0.02, 0.02);
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, jointMaterial);
    leftEyebrow.position.set(-0.15, 1.87, 0.45);
    leftEyebrow.name = 'leftEyebrow';
    robot.add(leftEyebrow);

    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, jointMaterial);
    rightEyebrow.position.set(0.15, 1.87, 0.45);
    rightEyebrow.name = 'rightEyebrow';
    robot.add(rightEyebrow);

    // Jaw - separate from mouth for realistic movement
    const jawGeometry = new THREE.BoxGeometry(0.15, 0.05, 0.08);
    const jaw = new THREE.Mesh(jawGeometry, shellMaterial);
    jaw.position.set(0, 1.6, 0.4);
    jaw.name = 'jaw';
    robot.add(jaw);

    // Mouth - part of jaw system
    const mouthGeometry = new THREE.BoxGeometry(0.12, 0.03, 0.02);
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
    mouth.position.set(0, 1.65, 0.45);
    mouth.name = 'mouth';
    robot.add(mouth);

    // Neck - visible mechanical joint for rotation
    const neckGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.25, 16);
    const neck = new THREE.Mesh(neckGeometry, jointMaterial);
    neck.position.y = 1.45;
    neck.name = 'neck';
    neck.rotation.order = 'XYZ';
    robot.add(neck);

    // Torso - White composite shell
    const torsoGeometry = new THREE.CylinderGeometry(0.4, 0.35, 0.8, 32);
    const torso = new THREE.Mesh(torsoGeometry, shellMaterial);
    torso.position.y = 0.9;
    torso.name = 'torso';
    robot.add(torso);

    // Transparent Core - visible inside torso
    const coreGeometry = new THREE.CylinderGeometry(0.2, 0.18, 0.5, 32);
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    core.position.y = 0.9;
    core.name = 'core';
    robot.add(core);

    // Chest button (Sonny's "brain" indicator)
    const chestLightGeometry = new THREE.CircleGeometry(0.1, 32);
    const chestLight = new THREE.Mesh(chestLightGeometry, eyeMaterial);
    chestLight.position.set(0, 1.1, 0.4);
    chestLight.name = 'chestLight';
    robot.add(chestLight);

    // Shoulders
    const shoulderGeometry = new THREE.SphereGeometry(0.2, 16, 16);
    const leftShoulder = new THREE.Mesh(shoulderGeometry, jointMaterial);
    leftShoulder.position.set(-0.5, 1.2, 0);
    robot.add(leftShoulder);

    const rightShoulder = new THREE.Mesh(shoulderGeometry, jointMaterial);
    rightShoulder.position.set(0.5, 1.2, 0);
    robot.add(rightShoulder);

    // Arms
    const armGeometry = new THREE.CylinderGeometry(0.08, 0.1, 0.6, 16);
    const leftArm = new THREE.Mesh(armGeometry, shellMaterial);
    leftArm.position.set(-0.65, 0.8, 0);
    leftArm.rotation.z = 0.2;
    leftArm.name = 'leftArm';
    robot.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, shellMaterial);
    rightArm.position.set(0.65, 0.8, 0);
    rightArm.rotation.z = -0.2;
    rightArm.name = 'rightArm';
    robot.add(rightArm);

    // Hands
    const handGeometry = new THREE.SphereGeometry(0.12, 16, 16);
    const leftHand = new THREE.Mesh(handGeometry, jointMaterial);
    leftHand.position.set(-0.75, 0.45, 0);
    leftHand.name = 'leftHand';
    robot.add(leftHand);

    const rightHand = new THREE.Mesh(handGeometry, jointMaterial);
    rightHand.position.set(0.75, 0.45, 0);
    rightHand.name = 'rightHand';
    robot.add(rightHand);

    // Hips
    const hipGeometry = new THREE.SphereGeometry(0.25, 16, 16);
    const hip = new THREE.Mesh(hipGeometry, jointMaterial);
    hip.position.y = 0.4;
    robot.add(hip);

    // Legs
    const legGeometry = new THREE.CylinderGeometry(0.12, 0.1, 0.7, 16);
    const leftLeg = new THREE.Mesh(legGeometry, shellMaterial);
    leftLeg.position.set(-0.2, 0.05, 0);
    robot.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeometry, shellMaterial);
    rightLeg.position.set(0.2, 0.05, 0);
    robot.add(rightLeg);

    // Feet
    const footGeometry = new THREE.BoxGeometry(0.15, 0.1, 0.25);
    const leftFoot = new THREE.Mesh(footGeometry, jointMaterial);
    leftFoot.position.set(-0.2, -0.35, 0.05);
    robot.add(leftFoot);

    const rightFoot = new THREE.Mesh(footGeometry, jointMaterial);
    rightFoot.position.set(0.2, -0.35, 0.05);
    robot.add(rightFoot);

    // Store references for animation
    (robot as any).robotParts = {
        head,
        leftEye,
        rightEye,
        mouth,
        jaw,
        chestLight,
        leftEyebrow,
        rightEyebrow,
        leftArm,
        rightArm,
        leftHand,
        rightHand,
        torso,
        neck,
        core,
    } as RobotParts;

    return robot;
}

// Animation state
let isTalking = false;
let talkStartTime = 0;
let expression = 'neutral';

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

// Animation function with Sonny-inspired movements
export function animateRobot(robot: THREE.Group, time: number): void {
    const parts = (robot as any).robotParts as RobotParts;
    if (!parts) return;

    const timeSeconds = time / 1000;

    // Breathing - subtle natural movement
    const breathDepth = 0.02;
    const breathSpeed = 1.5;
    robot.position.y = Math.sin(timeSeconds * breathSpeed) * breathDepth;

    // Core pulsing - transparency effect
    if (parts.core) {
        parts.core.scale.setScalar(1 + Math.sin(timeSeconds * 2) * 0.05);
        (parts.core.material as THREE.MeshStandardMaterial).emissiveIntensity = 
            0.5 + Math.sin(timeSeconds * 3) * 0.2;
    }

    // Eye glow pulsing
    [parts.leftEye, parts.rightEye].forEach(eye => {
        if (eye && eye instanceof THREE.Mesh) {
            (eye.material as THREE.MeshStandardMaterial).emissiveIntensity = 
                0.6 + Math.sin(timeSeconds * 3) * 0.2;
        }
    });

    // Jaw animation when talking
    if (parts.jaw) {
        if (isTalking) {
            const talkTime = (Date.now() - talkStartTime) / 1000;
            const jawOpen = Math.abs(Math.sin(talkTime * 12)) * 0.15;
            parts.jaw.rotation.x = jawOpen;
        } else {
            parts.jaw.rotation.x = 0;
        }
    }

    // Mouth animation
    if (parts.mouth) {
        if (isTalking) {
            const talkTime = (Date.now() - talkStartTime) / 1000;
            const mouthOpen = Math.abs(Math.sin(talkTime * 12)) * 0.08;
            parts.mouth.scale.y = 1 + mouthOpen;
        } else {
            parts.mouth.scale.y = 1;
        }
    }

    // Neck movement - independent from head
    if (parts.neck) {
        parts.neck.rotation.x = Math.sin(timeSeconds * 0.9) * 0.02;
        parts.neck.rotation.y = Math.sin(timeSeconds * 0.7) * 0.03;
    }

    // Head movement
    if (parts.head) {
        parts.head.rotation.x = Math.sin(timeSeconds * 0.8) * 0.03;
        parts.head.rotation.y = Math.sin(timeSeconds * 0.6) * 0.05;
    }

    // Facial expressions
    if (parts.leftEyebrow && parts.rightEyebrow) {
        switch (expression) {
            case 'listening':
                parts.leftEyebrow.rotation.z = -0.1;
                parts.rightEyebrow.rotation.z = 0.1;
                parts.leftEyebrow.position.y = 1.88;
                parts.rightEyebrow.position.y = 1.88;
                break;
            case 'thinking':
                parts.leftEyebrow.rotation.z = 0.3;
                parts.rightEyebrow.rotation.z = -0.3;
                parts.leftEyebrow.position.y = 1.86;
                parts.rightEyebrow.position.y = 1.86;
                break;
            case 'researching':
                parts.leftEyebrow.rotation.z = -0.05;
                parts.rightEyebrow.rotation.z = 0.05;
                parts.leftEyebrow.position.y = 1.88;
                parts.rightEyebrow.position.y = 1.88;
                break;
            case 'analyzing':
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.87;
                parts.rightEyebrow.position.y = 1.87;
                break;
            case 'speaking':
                parts.leftEyebrow.rotation.z = -0.15 + Math.sin(timeSeconds * 2) * 0.02;
                parts.rightEyebrow.rotation.z = 0.15 - Math.sin(timeSeconds * 2) * 0.02;
                parts.leftEyebrow.position.y = 1.87 + Math.sin(timeSeconds * 3) * 0.01;
                parts.rightEyebrow.position.y = 1.87 + Math.sin(timeSeconds * 3) * 0.01;
                break;
            case 'concerned':
                parts.leftEyebrow.rotation.z = 0.35;
                parts.rightEyebrow.rotation.z = -0.35;
                parts.leftEyebrow.position.y = 1.85;
                parts.rightEyebrow.position.y = 1.85;
                break;
            case 'alert':
                parts.leftEyebrow.rotation.z = 0.4;
                parts.rightEyebrow.rotation.z = -0.4;
                parts.leftEyebrow.position.y = 1.89;
                parts.rightEyebrow.position.y = 1.89;
                break;
            case 'focused':
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.87;
                parts.rightEyebrow.position.y = 1.87;
                break;
            case 'idle':
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.87;
                parts.rightEyebrow.position.y = 1.87;
                break;
            default: // neutral
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.87;
                parts.rightEyebrow.position.y = 1.87;
        }
    }

    // Eye shape and blinking
    if (parts.leftEye && parts.rightEye) {
        let eyeScaleX = 1.0;
        let blinkRate = 2;
        
        switch (expression) {
            case 'alert': eyeScaleX = 1.15; blinkRate = 4; break;
            case 'concerned': eyeScaleX = 0.9; blinkRate = 1.5; break;
            case 'focused': eyeScaleX = 1.05; blinkRate = 3; break;
            case 'researching': eyeScaleX = 1.1; blinkRate = 2.5; break;
            case 'thinking': eyeScaleX = 0.9; blinkRate = 1.5; break;
        }
        
        const blink = Math.sin(timeSeconds * blinkRate) > 0.95 ? 0.1 : 1;
        parts.leftEye.scale.x = eyeScaleX * blink;
        parts.rightEye.scale.x = eyeScaleX * blink;
    }

    // Arm movements - subtle natural motion
    const leftArm = robot.children.find(c => c.name === 'leftArm');
    const rightArm = robot.children.find(c => c.name === 'rightArm');
    
    if (leftArm && rightArm) {
        leftArm.rotation.z = 0.2 + Math.sin(timeSeconds * 1) * 0.05;
        rightArm.rotation.z = -0.2 - Math.sin(timeSeconds * 1) * 0.05;
    }
}