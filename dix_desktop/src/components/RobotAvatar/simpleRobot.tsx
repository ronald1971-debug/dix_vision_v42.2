// Normal Proportioned Robot Avatar - Code-Based Generation
// This creates a normal-sized robot using Three.js primitives
// Sonny-inspired design from I, Robot
// Includes a sign that the robot can hold

import * as THREE from 'three';

export interface RobotParts {
    head: THREE.Mesh;
    leftEye: THREE.Mesh;
    rightEye: THREE.Mesh;
    mouth: THREE.Mesh;
    chestLight: THREE.Mesh;
    leftEyebrow: THREE.Mesh;
    rightEyebrow: THREE.Mesh;
    leftArm: THREE.Mesh;
    rightArm: THREE.Mesh;
    leftHand: THREE.Mesh;
    rightHand: THREE.Mesh;
    torso: THREE.Mesh;
    sign: THREE.Mesh;
    signText: THREE.Mesh;
}

export interface GestureState {
    type: 'idle' | 'talking' | 'explaining' | 'greeting' | 'thinking' | 'excited' | 'questioning';
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

    const mouthMaterial = new THREE.MeshStandardMaterial({
        color: 0x2a2a2a, // Dark gray for contrast
        emissive: 0x000000,
        emissiveIntensity: 0.0,
        metalness: 0.6,
        roughness: 0.4,
    });

    const signMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFFFFF, // White sign
        metalness: 0.1,
        roughness: 0.2,
    });

    // Head
    const headGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const head = new THREE.Mesh(headGeometry, bodyMaterial);
    head.position.y = 1.7;
    head.name = 'head';
    robot.add(head);

    // Eyes (Sonny-style glowing blue - normal size)
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

    // Mouth (normal proportion, visible but not exaggerated)
    const mouthGeometry = new THREE.BoxGeometry(0.12, 0.04, 0.03);
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
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
    torso.name = 'torso';
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
    leftArm.name = 'leftArm';
    robot.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, bodyMaterial);
    rightArm.position.set(0.65, 0.8, 0);
    rightArm.rotation.z = -0.2;
    rightArm.name = 'rightArm';
    robot.add(rightArm);

    // Hands
    const handGeometry = new THREE.SphereGeometry(0.12, 16, 16);
    const leftHand = new THREE.Mesh(handGeometry, darkMaterial);
    leftHand.position.set(-0.75, 0.45, 0);
    leftHand.name = 'leftHand';
    robot.add(leftHand);

    const rightHand = new THREE.Mesh(handGeometry, darkMaterial);
    rightHand.position.set(0.75, 0.45, 0);
    rightHand.name = 'rightHand';
    robot.add(rightHand);

    // SIGN - white sign that the robot can hold
    const signGeometry = new THREE.BoxGeometry(0.6, 0.4, 0.02);
    const sign = new THREE.Mesh(signGeometry, signMaterial);
    sign.position.set(0.9, 1.0, 0.2);
    sign.name = 'sign';
    robot.add(sign);

    // Sign text (simple stripe)
    const textGeometry = new THREE.BoxGeometry(0.5, 0.1, 0.03);
    const text = new THREE.Mesh(textGeometry, darkMaterial);
    text.position.set(0.9, 1.1, 0.25);
    text.name = 'signText';
    robot.add(text);

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
        leftArm,
        rightArm,
        leftHand,
        rightHand,
        torso,
        sign,
        signText,
    } as RobotParts;

    // Initialize rotation tracking
    currentRotations = {
        head: new THREE.Euler(),
        torso: new THREE.Euler(),
        leftArm: new THREE.Euler(),
        rightArm: new THREE.Euler(),
        leftHand: new THREE.Euler(),
        rightHand: new THREE.Euler(),
        sign: new THREE.Euler(),
    };

    return robot;
}

// Animation state for talking
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
            targets.sign = new THREE.Euler(0, 0, 0.5);
            targets.head = new THREE.Euler(0.1, 0.2, 0);
            break;
        case 'questioning':
            targets.rightArm = new THREE.Euler(0.4, -0.2, -0.3);
            targets.leftArm = new THREE.Euler(0.1, 0.1, 0.2);
            targets.sign = new THREE.Euler(0, 0, 0.3);
            targets.head = new THREE.Euler(0.2, 0.3, 0.1);
            break;
        case 'excited':
            targets.leftArm = new THREE.Euler(0.5, 0.5, 0.8);
            targets.rightArm = new THREE.Euler(0.5, -0.5, -0.8);
            targets.sign = new THREE.Euler(0, 0, 0.8);
            targets.head = new THREE.Euler(0.2, 0, 0);
            break;
        case 'explaining':
            targets.rightArm = new THREE.Euler(0.3, -0.3, -0.4);
            targets.leftArm = new THREE.Euler(0.1, 0.1, 0.2);
            targets.sign = new THREE.Euler(0, 0, 0.4);
            targets.head = new THREE.Euler(0.1, 0.1, 0);
            break;
        case 'thinking':
            targets.rightArm = new THREE.Euler(0.6, -0.2, -0.2);
            targets.sign = new THREE.Euler(0.3, 0, 0.5);
            targets.leftArm = new THREE.Euler(0.1, 0.1, 0.1);
            targets.head = new THREE.Euler(0.3, 0, 0);
            break;
        case 'talking':
        default:
            targets.leftArm = new THREE.Euler(0.1 + intensity * 0.2, 0.1 + intensity * 0.1, 0.2 + intensity * 0.1);
            targets.rightArm = new THREE.Euler(-0.1 - intensity * 0.2, -0.1 - intensity * 0.1, -0.2 - intensity * 0.1);
            targets.sign = new THREE.Euler(0, 0, 0.2);
            targets.head = new THREE.Euler(0.05, 0.05, 0);
            break;
    }

    return targets;
}

// Animation function
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

    // Get target rotations based on current gesture
    const targets = getTargetRotationsForGesture(currentGesture);

    // Smoothly interpolate to target rotations
    const lerpSpeed = 0.05;
    Object.keys(targets).forEach(key => {
        if (!currentRotations[key]) {
            currentRotations[key] = new THREE.Euler();
        }
        currentRotations[key] = lerpEuler(currentRotations[key], targets[key], lerp);
    });

    // Apply rotations to body parts
    if (parts.head) {
        parts.head.rotation.x = currentRotations.head.x + Math.sin(timeSeconds * 0.8) * 0.03;
        parts.head.rotation.y = currentRotations.head.y + Math.sin(timeSeconds * 0.6) * 0.05;
        parts.head.rotation.z = currentRotations.head.z + Math.sin(timeSeconds * 0.7) * 0.02;
    }

    if (parts.torso) {
        parts.torso.rotation.x = currentRotations.torso.x + Math.sin(timeSeconds * 1.2) * 0.02;
        parts.torso.rotation.y = currentRotations.torso.y + Math.sin(timeSeconds * 0.9) * 0.03;
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

    // Sign animation
    if (parts.sign) {
        parts.sign.rotation.x = currentRotations.sign.x + Math.sin(timeSeconds * 0.8) * 0.05;
        parts.sign.rotation.y = currentRotations.sign.y + Math.sin(timeSeconds * 0.6) * 0.05;
    }

    // Hand movements
    if (parts.leftHand) {
        const handWave = isTalking ? Math.sin(timeSeconds * 8) * 0.1 : 0;
        parts.leftHand.position.y = 0.45 + handWave;
    }

    if (parts.rightHand) {
        const handWave = isTalking ? Math.sin(timeSeconds * 8 + Math.PI) * 0.1 : 0;
        parts.rightHand.position.y = 0.45 + handWave;
    }

    // Eye glow pulsing
    [parts.leftEye, parts.rightEye].forEach(eye => {
        if (eye && eye instanceof THREE.Mesh) {
            const baseIntensity = 0.6;
            const pulseAmount = currentGesture.type === 'excited' ? 0.4 : 0.2;
            (eye.material as THREE.MeshStandardMaterial).emissiveIntensity = 
                baseIntensity + Math.sin(timeSeconds * 3) * pulseAmount;
        }
    });

    // Mouth animation when talking
    if (parts.mouth) {
        if (isTalking) {
            const talkTime = (Date.now() - talkStartTime) / 1000;
            const mouthOpen = Math.abs(Math.sin(talkTime * 12)) * 0.08 + 
                            Math.abs(Math.sin(talkTime * 7)) * 0.04;
            parts.mouth.scale.y = 1 + mouthOpen;
            parts.mouth.position.y = 1.6 - mouthOpen * 0.3;
            parts.mouth.rotation.x = mouthOpen * 0.1;
        } else {
            parts.mouth.scale.y = 1;
            parts.mouth.position.y = 1.6;
            parts.mouth.rotation.x = 0;
        }
    }

    // Facial expressions
    if (parts.leftEyebrow && parts.rightEyebrow) {
        switch (expression) {
            case 'happy':
                parts.leftEyebrow.rotation.z = -0.2 + Math.sin(timeSeconds * 2) * 0.02;
                parts.rightEyebrow.rotation.z = 0.2 - Math.sin(timeSeconds * 2) * 0.02;
                parts.leftEyebrow.position.y = 1.83 + Math.sin(timeSeconds * 3) * 0.01;
                parts.rightEyebrow.position.y = 1.83 + Math.sin(timeSeconds * 3) * 0.01;
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

    // Eye shape changes
    if (parts.leftEye && parts.rightEye) {
        const eyeScaleX = expression === 'happy' ? 1.3 : 
                         expression === 'sad' ? 0.8 : 
                         expression === 'surprised' ? 1.2 : 1;
        const blinkRate = expression === 'surprised' ? 4 : 2;
        const blink = Math.sin(timeSeconds * blinkRate) > 0.95 ? 0.1 : 1;
        parts.leftEye.scale.x = eyeScaleX * blink;
        parts.rightEye.scale.x = eyeScaleX * blink;
    }

    // Weight shifting
    const weightShift = Math.sin(timeSeconds * 0.8) * 0.02;
    robot.position.x = weightShift;

    // Subtle knee bend
    const leftLeg = robot.children[robot.children.length - 4];
    const rightLeg = robot.children[robot.children.length - 3];
    if (leftLeg && rightLeg) {
        leftLeg.rotation.x = weightShift * 0.1;
        rightLeg.rotation.x = -weightShift * 0.1;
    }

    // Gesture timeout
    if (currentGesture.type !== 'idle' && gestureAge > 8) {
        currentGesture = { type: 'idle', intensity: 0, startTime: Date.now() };
    }
}