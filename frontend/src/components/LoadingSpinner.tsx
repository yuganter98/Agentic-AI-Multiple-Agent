"use client";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export function LoadingSpinner({ size = 24 }: { size?: number }) {
    return (
        <motion.div
            animate={{ rotate: 360 }}
            transition={{ ease: "linear", duration: 1, repeat: Infinity }}
            className="inline-flex items-center justify-center text-blue-500"
        >
            <Loader2 size={size} strokeWidth={2.5} />
        </motion.div>
    );
}
