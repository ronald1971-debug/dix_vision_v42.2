// Sonny-Inspired Robot Avatar - Enhanced Design
// Based on DIXVISION v42.2 Architecture Requirements
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
    neckJoint: THREE.Mesh;
    leftShoulderJoint: THREE.Mesh;
    rightShoulderJoint: THREE.Mesh;
    leftElbowJoint: THREE.Mesh;
    rightElbowJoint: THREE.Mesh;
}

export interface GestureState {
    type: 'idle' | 'talking' | 'explaining' | 'greeting' | 'thinking' | 'excited' | 'questioning' | 'listening' | 'researching' | 'analyzing' | 'concerned' | 'alert' | 'focused';
    intensity: number;
    startTime: number;
}

export function analyzeGesture(text: string): GestureState {
    const lowerText = text.toLowerCase();
    
    if (lowerText.match(/^(hello|hi|hey|good morning|good evening|greetings)/i)) {
        return { type: 'greeting', intensity: 0.8, startTime: Date.now() };
    }
    
    if (lowerText.includes('?') || lowerText.match(/(what|how|why|when|where|who|which|can you|could you)/i)) {
        return { type: 'questioning', intensity: 0.7, startTime: Date.now() };
    }
    
    if (lowerText.match(/(excellent|great|amazing|wonderful|fantastic|awesome|exciting|!+)/i)) {
        return { type: 'excited', intensity: 0.9, startTime: Date.now() };
    }
    
    if (lowerText.match(/(let me explain|basically|essentially|in other words|what i mean|think about|consider)/i)) {
        return { type: 'explaining', intensity: 0.6, startTime: Date.now() };
    }
    
    if (lowerText.match(/(let me think|hmm|interesting|i wonder|perhaps|maybe)/i)) {
        return { type: 'thinking', intensity: 0.5, startTime: Date.now() };
    }

    if (lowerText.match(/(i'm listening|tell me more|go ahead|continue)/i)) {
        return { type: 'listening', intensity: 0.4, startTime: Date.now() };
    }

    if (lowerText.match(/(researching|looking into|investigating|studying)/i)) {
        return { type: 'researching', intensity: 0.5, startTime: Date.now() };
    }

    if (lowerText.match(/(analyzing|analyzing data|processing|calculating)/i)) {
        return { type: 'analyzing', intensity: 0.6, startTime: Date.now() };
    }

    if (lowerText.match(/(concerned|worried|caution|warning|alert)/i)) {
        return { type: 'concerned', intensity: 0.7, startTime: Date.now() };
    }

    if (lowerText.match(/(alert|emergency|urgent|immediate)/i)) {
        return { type: 'alert', intensity: 0.9, startTime: Date.now() };
    }

    if (lowerText.match(/(focused|concentrating|paying attention)/i)) {
        return { type: 'focused', intensity: 0.6, startTime: Date.now() };
    }
    
    return { type: 'talking', intensity: 0.4, startTime: Date.now() };
}

let currentGesture: GestureState = { type: 'idle', intensity: 0, startTime: 0 };
let targetRotations: { [key: string]: THREE.Euler } = {};
let currentRotations: { [key: string]: THREE.Euler } = {};

export function setGesture(gesture: GestureState) {
    currentGesture = gesture;
}

export function createSimpleRobot(): THREE.Group {
    const robot = new THREE.Group();

    // Materials - Sonny-inspired White Composite Shell
    const shellMaterial = new THREE.MeshStandardMaterial({
        color: 0xF0F0F0, // White composite shell
        metalness: 0.8,
        roughness: 0.15,
    });

    const jointMaterial = new THREE.MeshStandardMaterial({
        color: 0x2a2a2a, // Dark mechanical joints
        metalness: 0.95,
        roughness: 0.05,
    });

    const eyeMaterial = new THREE.MeshStandardMaterial({
        color: 0x00BFFF, // Glowing blue eyes
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
        opacity: 0.7,
    });

    // Head - White composite shell
    const headGeometry = new THREE.SphereGeometry(0.48, 32, 32);
    const head = new THREE.Mesh(headGeometry, shellMaterial);
    head.position.y = 1.7;
    head.name = 'head';
    robot.add(head);

    // Eyes - Glowing blue, normal size
    const eyeGeometry = new THREE.SphereGeometry(0.07, 16, 16);
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.15, 1.75, 0.4);
    leftEye.name = 'leftEye';
    robot.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.15, 1.75, 0.4);
    rightEye.name = 'rightEye';
    robot.add(rightEye);

    // Eyebrows
    const eyebrowGeometry = new THREE.BoxGeometry(0.15, 0.02, 0.02);
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, jointMaterial);
    leftEyebrow.position.set(-0.15, 1.82, 0.45);
    leftEyebrow.name = 'leftEyebrow';
    robot.add(leftEyebrow);

    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, jointMaterial);
    rightEyebrow.position.set(0.15, 1.82, 0.45);
    rightEyebrow.name = 'rightEyebrow';
    robot.add(rightEyebrow);

    // Jaw mechanism - separate from mouth
    const jawGeometry = new THREE.BoxGeometry(0.15, 0.05, 0.08);
    const jaw = new THREE.Mesh(jawGeometry, shellMaterial);
    jaw.position.set(0, 1.55, 0.4);
    jaw.name = 'jaw';
    robot.add(jaw);

    // Mouth - part of jaw system
    const mouthGeometry = new THREE.BoxGeometry(0.10, 0.03, 0.02);
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
    mouth.position.set(0, 1.6, 0.45);
    mouth.name = 'mouth';
    robot.add(mouth);

    // Neck - visible mechanical joint
    const neckGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.25, 16);
    const neck = new THREE.Mesh(neckGeometry, jointMaterial);
    neck.position.y = 1.4;
    neck.name = 'neck';
    neck.rotation.order = 'XYZ';
    robot.add(neck);

    // Neck joint sphere
    const neckJointGeometry = new THREE.SphereGeometry(0.13, 16, 16);
    const neckJoint = new THREE.Mesh(neckJointGeometry, jointMaterial);
    neckJoint.position.y = 1.5;
    neckJoint.name = 'neckJoint';
    robot.add(neckJoint);

    // Torso - White composite shell
    const torsoGeometry = new THREE.CylinderGeometry(0.4, 0.35, 0.8, 32);
    const torso = new THREE.Mesh(torsoGeometry, shellMaterial);
    torso.position.y = 0.9;
    torso.name = 'torso';
    robot.add(torso);

    // Transparent Core - visible inside torso
    const coreGeometry = new THREE.CylinderGeometry(0.25, 0.2, 0.6, 32);
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

    // Shoulders with joint spheres
    const shoulderGeometry = new THREE.SphereGeometry(0.2, 16, 16);
    const leftShoulder = new THREE.Mesh(shoulderGeometry, jointMaterial);
    leftShoulder.position.set(-0.5, 1.2, 0);
    robot.add(leftShoulder);

    const rightShoulder = new THREE.Mesh(shoulderGeometry, jointMaterial);
    rightShoulder.position.set(0.5, 1.2, 0);
    robot.add(rightShoulder);

    // Shoulder joint spheres
    const leftShoulderJointGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    const leftShoulderJoint = new THREE.Mesh(leftShoulderJointGeometry, jointMaterial);
    leftShoulderJoint.position.set(-0.5, 1.25, 0);
    leftShoulderJoint.name = 'leftShoulderJoint';
    robot.add(leftShoulderJoint);

    const rightShoulderJointGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    const rightShoulderJoint = new THREE.Mesh(rightShoulderJointGeometry, jointMaterial);
    rightShoulderJoint.position.set(0.5, 1.25, 0);
    rightShoulderJoint.name = 'rightShoulderJoint';
    robot.add(rightShoulderJoint);

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

    // Elbow joint spheres
    const leftElbowJointGeometry = new THREE.SphereGeometry(0.12, 16, 16);
    const leftElbowJoint = new THREE.Mesh(leftElbowJointGeometry, jointMaterial);
    leftElbowJoint.position.set(-0.65, 0.5, 0);
    leftElbowJoint.name = 'leftElbowJoint';
    robot.add(leftElbowJoint);

    const rightElbowJointGeometry = new THREE.SphereGeometry(0.12, 16, 16);
    const rightElbowJoint = new THREE.Mesh(rightElbowJointGeometry, jointMaterial);
    rightElbowJoint.position.set(0.65, 0.5, 0);
    rightElbowJoint.name = 'rightElbowJoint';
    robot.add(rightElbowJoint);

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
        neckJoint,
        leftShoulderJoint,
        rightShoulderJoint,
        leftElbowJoint,
        rightElbowJoint,
    } as RobotParts;

    // Initialize rotation tracking
    currentRotations = {
        head: new THREE.Euler(),
        neck: new THREE.Euler(),
        torso: new THREE.Euler(),
        leftArm: new THREE.Euler(),
        rightArm: new THREE.Euler(),
        jaw: new THREE.Euler(),
    };

    return robot;
}

// Animation state
let isTalking = false;
let talkStartTime = 0;
let expression = 'neutral';
let mouseX = 0;
let mouseY = 0;

export function setTalking(talking: boolean) {
    isTalking = talking;
    if (talking) {
        talkStartTime = Date.now();
    }
}

export function setExpression(newExpression: string) {
    expression = newExpression;
}

export function setMousePosition(x: number, y: number) {
    mouseX = x;
    mouseY = y;
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

// Smooth interpolation
function lerp(start: number, end: number, t: number): number {
    return start + (end - start) * t;
}

function lerpEuler(current: THREE.Euler, target: THREE.Euler, t: number): THREE.Euler {
    return new THREE.Euler(
        lerp(current.x, target.x, t),
        lerp(current.y, target.y, t),
        lerp(current.z, target.z, t)
    );
}

// Get target rotations based on gesture
function getTargetRotationsForGesture(gesture: GestureState): { [key: string]: THREE.Euler } {
    const intensity = gesture.intensity;
    const targets: { [key: string]: THREE.Euler } = {};

    switch (gesture.type) {
        case 'greeting':
            targets.leftArm = new THREE.Euler(0.3, 0.3, 0.5);
            targets.rightArm = new THREE.Euler(0.3, -0.3, -0.5);
            targets.head = new THREE.Euler(0.1, 0.2, 0);
            targets.neck = new THREE.Euler(0.1, 0.1, 0);
            break;
        case 'questioning':
            targets.rightArm = new THREE.Euler(0.4, -0.2, -0.3);
            targets.leftArm = new THREE.Euler(0.1, 0.1, 0.2);
            targets.head = new THREE.Euler(0.2, 0.3, 0.1);
            targets.neck = new THREE.Euler(0.1, 0.15, 0.05);
            break;
        case 'listening':
            targets.head = new THREE.Euler(0.0, 0.2, 0.15);
            targets.neck = new THREE.Euler(0.0, 0.15, 0.1);
            break;
        case 'thinking':
            targets.rightArm = new THREE.Euler(0.6, -0.2, -0.2);
            targets.head = new THREE.Euler(0.3, 0.0, 0);
            targets.neck = new THREE.Euler(0.2, 0.0, 0);
            targets.jaw = new THREE.Euler(0.1, 0, 0);
            break;
        case 'researching':
            targets.head = new THREE.Euler(0.1, 0.3, 0);
            targets.neck = new THREE.Euler(0.05, 0.2, 0);
            break;
        case 'analyzing':
            targets.head = new THREE.Euler(0.0, 0.1, 0);
            targets.neck = new THREE.Euler(0.0, 0.05, 0);
            break;
        case 'concerned':
            targets.head = new THREE.Euler(0.1, 0.0, 0.1);
            targets.neck = new THREE.Euler(0.05, 0.0, 0.05);
            break;
        case 'alert':
            targets.head = new THREE.Euler(0.2, 0.0, 0);
            targets.neck = new THREE.Euler(0.1, 0.0, 0);
            break;
        case 'focused':
            targets.head = new THREE.Euler(0.0, 0.05, 0);
            targets.neck = new THREE.Euler(0.0, 0.03, 0);
            break;
        case 'excited':
            targets.leftArm = new THREE.Euler(0.5, 0.5, 0.8);
            targets.rightArm = new THREE.Euler(0.5, -0.5, -0.8);
            targets.head = new THREE.Euler(0.2, 0, 0);
            break;
        case 'explaining':
            targets.rightArm = new THREE.Euler(0.3, -0.3, -0.4);
            targets.leftArm = new THREE.Euler(0.1, 0.1, 0.2);
            targets.head = new THREE.Euler(0.1, 0.1, 0);
            break;
        case 'talking':
        default:
            targets.leftArm = new THREE.Euler(0.1 + intensity * 0.2, 0.1 + intensity * 0.1, 0.2 + intensity * 0.1);
            targets.rightArm = new THREE.Euler(-0.1 - intensity * 0.2, -0.1 - intensity * 0.1, -0.2 - intensity * 0.1);
            targets.head = new THREE.Euler(0.05, 0.05, 0);
            targets.neck = new THREE.Euler(0.02, 0.02, 0);
            break;
    }

    return targets;
}

// Enhanced animation function
export function animateRobot(robot: THREE.Group, time: number): void {
    const parts = (robot as any).robotParts as RobotParts;
    if (!parts) return;

    const timeSeconds = time / 1000;
    const gestureAge = (Date.now() - currentGesture.startTime) / 1000;

    // Breathing - subtle full-body movement
    const breathDepth = 0.02;
    const breathSpeed = 1.5;
    robot.position.y = Math.sin(timeSeconds * breathSpeed) * breathDepth;
    robot.scale.y = 1 + Math.sin(timeSeconds * breathSpeed) * 0.01;

    // Core pulsing
    if (parts.core) {
        parts.core.scale.setScalar(1 + Math.sin(timeSeconds * 2) * 0.05);
        (parts.core.material as THREE.MeshStandardMaterial).emissiveIntensity = 
            0.5 + Math.sin(timeSeconds * 3) * 0.2;
    }

    // Get target rotations
    const targets = getTargetRotationsForGesture(currentGesture);

    // Smoothly interpolate
    const lerpSpeed = 0.05;
    Object.keys(targets).forEach(key => {
        if (!currentRotations[key]) {
            currentRotations[key] = new THREE.Euler();
        }
        currentRotations[key] = lerpEuler(currentRotations[key], targets[key], lerpSpeed);
    });

    // Apply rotations
    if (parts.head) {
        parts.head.rotation.x = currentRotations.head.x + Math.sin(timeSeconds * 0.8) * 0.03;
        parts.head.rotation.y = currentRotations.head.y + Math.sin(timeSeconds * 0.6) * 0.05;
        parts.head.rotation.z = currentRotations.head.z + Math.sin(timeSeconds * 0.7) * 0.02;
    }

    if (parts.neck) {
        parts.neck.rotation.x = currentRotations.neck.x + Math.sin(timeSeconds * 0.9) * 0.02;
        parts.neck.rotation.y = currentRotations.neck.y + Math.sin(timeSeconds * 0.7) * 0.03;
        parts.neck.rotation.z = currentRotations.neck.z + Math.sin(timeSeconds * 0.8) * 0.01;
    }

    if (parts.jaw) {
        if (isTalking) {
            const talkTime = (Date.now() - talkStartTime) / 1000;
            const jawOpen = Math.abs(Math.sin(talkTime * 12)) * 0.15;
            parts.jaw.rotation.x = currentRotations.jaw.x + jawOpen;
        } else {
            parts.jaw.rotation.x = currentRotations.jaw.x;
        }
    }

    if (parts.leftArm) {
        parts.leftArm.rotation.x = currentRotations.leftArm.x + Math.sin(timeSeconds * 1.5) * 0.05;
        parts.leftArm.rotation.y = currentRotations.leftArm.y + Math.sin(timeSeconds * 1.3) * 0.03;
        parts.leftArm.rotation.z = currentRotations.leftArm.z + Math.sin(timeSeconds * 1.1) * 0.04;
    }

    if (parts.rightArm) {
        parts.rightArm.rotation.x = currentRotations.rightArm.x + Math.sin(timeSeconds * 1.4) * 0.05;
        parts.rightArm.rotation.y = currentRotations.rightArm.y + Math.sin(timeSeconds * 1.2) * 0.03;
        parts.rightArm.rotation.z = currentRotations.rightArm.z + Math.sin(timeSeconds * 1.0) * 0.04;
    }

    // Eye tracking - follow mouse
    if (parts.leftEye && parts.rightEye) {
        const lookX = (mouseX - window.innerWidth/2) / window.innerWidth;
        const lookY = -(mouseY - window.innerHeight/2) / window.innerHeight;
        
        parts.leftEye.rotation.y = lookX * 0.3;
        parts.leftEye.rotation.x = lookY * 0.3;
        parts.rightEye.rotation.y = lookX * 0.3;
        parts.rightEye.rotation.x = lookY * 0.3;
    }

    // Eye glow
    [parts.leftEye, parts.rightEye].forEach(eye => {
        if (eye && eye instanceof THREE.Mesh) {
            const baseIntensity = 0.6;
            const pulseAmount = currentGesture.type === 'alert' ? 0.4 : 0.2;
            (eye.material as THREE.MeshStandardMaterial).emissiveIntensity = 
                baseIntensity + Math.sin(timeSeconds * 3) * pulseAmount;
        }
    });

    // Mouth animation
    if (parts.mouth) {
        if (isTalking) {
            const talkTime = (Date.now() - talkStartTime) / 1000;
            const mouthOpen = Math.abs(Math.sin(talkTime * 12)) * 0.08 + 
                            Math.abs(Math.sin(talkTime * 7)) * 0.04;
            parts.mouth.scale.y = 1 + mouthOpen;
        } else {
            parts.mouth.scale.y = 1;
        }
    }

    // Enhanced facial expressions
    if (parts.leftEyebrow && parts.rightEyebrow) {
        switch (expression) {
            case 'listening':
                parts.leftEyebrow.rotation.z = -0.1;
                parts.rightEyebrow.rotation.z = 0.1;
                parts.leftEyebrow.position.y = 1.83;
                parts.rightEyebrow.position.y = 1.83;
                break;
            case 'thinking':
                parts.leftEyebrow.rotation.z = 0.3;
                parts.rightEyebrow.rotation.z = -0.3;
                parts.leftEyebrow.position.y = 1.84;
                parts.rightEyebrow.position.y = 1.84;
                break;
            case 'researching':
                parts.leftEyebrow.rotation.z = -0.05;
                parts.rightEyebrow.rotation.z = 0.05;
                parts.leftEyebrow.position.y = 1.83;
                parts.rightEyebrow.position.y = 1.83;
                break;
            case 'analyzing':
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.82;
                parts.rightEyebrow.position.y = 1.82;
                break;
            case 'concerned':
                parts.leftEyebrow.rotation.z = 0.35;
                parts.rightEyebrow.rotation.z = -0.35;
                parts.leftEyebrow.position.y = 1.81;
                parts.rightEyebrow.position.y = 1.81;
                break;
            case 'alert':
                parts.leftEyebrow.rotation.z = 0.4;
                parts.rightEyebrow.rotation.z = -0.4;
                parts.leftEyebrow.position.y = 1.85;
                parts.rightEyebrow.position.y = 1.85;
                break;
            case 'focused':
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.82;
                parts.rightEyebrow.position.y = 1.82;
                break;
            default:
                parts.leftEyebrow.rotation.z = 0;
                parts.rightEyebrow.rotation.z = 0;
                parts.leftEyebrow.position.y = 1.82;
                parts.rightEyebrow.position.y = 1.82;
        }
    }

    // Eye shape based on expression
    if (parts.leftEye && parts.rightEye) {
        let eyeScaleX = 1.0;
        let blinkRate = 2;
        
        switch (expression) {
            case 'happy': eyeScaleX = 1.3; blinkRate = 3; break;
            case 'sad': eyeScaleX = 0.8; blinkRate = 2; break;
            case 'surprised': eyeScaleX = 1.2; blinkRate = 4; break;
            case 'concerned': eyeScaleX = 0.9; blinkRate = 1.5; break;
            case 'alert': eyeScaleX = 1.15; blinkRate = 5; break;
            case 'focused': eyeScaleX = 1.05; blinkRate = 3; break;
            case 'researching': eyeScaleX = 1.1; blinkRate = 2.5; break;
        }
        
        const blink = Math.sin(timeSeconds * blinkRate) > 0.95 ? 0.1 : 1;
        parts.leftEye.scale.x = eyeScaleX * blink;
        parts.rightEye.scale.x = eyeScaleX * blink;
    }

    // Weight shifting
    const weightShift = Math.sin(timeSeconds * 0.8) * 0.02;
    robot.position.x = weightShift;

    // Gesture timeout
    if (currentGesture.type !== 'idle' && gestureAge > 8) {
        currentGesture = { type: 'idle', intensity: 0, startTime: Date.now() };
    }
}