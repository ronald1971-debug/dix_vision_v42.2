"use client";

import { motion, type Variants } from "framer-motion";

interface EaseTransitionProps {
  children: React.ReactNode;
  duration?: number;
  delay?: number;
  className?: string;
}

const organicVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 14,
    filter: "blur(6px)",
  },
  show: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.85,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

export function EaseTransition({
  children,
  duration = 0.85,
  delay = 0,
  className = "",
}: EaseTransitionProps) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      animate="show"
      transition={{
        duration,
        delay,
      }}
      variants={organicVariants}
    >
      {children}
    </motion.div>
  );
}
