import AgentIcon from "@/assets/icons/agent.svg?url";
import { useEffect, useMemo, useRef, useState } from "react";
import PopupGateway from "../Popup";
import { VoteIn } from "../VoteIn";
import { VoteOut } from "../VoteOut";
import styles from "./PropositionAgent.module.scss";

// Import all available icons
import ChatGptIcon from "@/assets/icons/chat-gpt.svg?url";
import ClaudeIcon from "@/assets/icons/claude.svg?url";
import DeepSeekIcon from "@/assets/icons/deepseek.svg?url";
import GeminiIcon from "@/assets/icons/gemini.svg?url";
import GrokIcon from "@/assets/icons/grok.svg?url";
import MistralIcon from "@/assets/icons/mistral.svg?url";

// Map icon names to their imports
const iconMap: Record<string, string> = {
  "chat-gpt": ChatGptIcon,
  "claude": ClaudeIcon,
  "gemini": GeminiIcon,
  "deepseek": DeepSeekIcon,
  "grok": GrokIcon,
  "mistral": MistralIcon,
};

interface PropositionAgentProps {
  id: string;
  name: string;
  icon?: string;
  isActive?: boolean;
  isSpeaking?: boolean;
  voteStatus?: "in" | "out" | null;
  voteCast?: { vote: "in" | "out"; reasoning: string } | null;
  streamingContent?: string;
  angle?: number;
  radius?: number;
  phase?: "debating" | "voting";
}

export function PropositionAgent({
  name,
  icon,
  angle = 0,
  isSpeaking = false,
  streamingContent = "",
  voteCast,
  phase = "debating",
}: PropositionAgentProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const previousContentRef = useRef("");

  // Get icon URL - use configured icon if available, otherwise fallback to default
  const iconUrl = useMemo(() => {

    if (icon && iconMap[icon]) {
      return iconMap[icon];
    }
    return AgentIcon;
  }, [icon, isSpeaking]);

  // Typing animation effect
  useEffect(() => {
    // Reset if content changed completely (new message)
    if (streamingContent !== previousContentRef.current) {
      // If it's a completely new message (not just more content), reset
      if (
        streamingContent.length < previousContentRef.current.length ||
        !streamingContent.startsWith(previousContentRef.current)
      ) {
        setDisplayedText("");
        previousContentRef.current = "";
      }
    }

    // If we have new content to display
    if (streamingContent && displayedText.length < streamingContent.length) {
      setIsTyping(true);

      // Clear any existing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      // Type out characters one by one
      const nextChar = streamingContent[displayedText.length];
      if (nextChar) {
        typingTimeoutRef.current = setTimeout(() => {
          setDisplayedText(streamingContent.slice(0, displayedText.length + 1));
        }, 30); // 30ms per character for typing speed
      }
    } else if (
      displayedText.length === streamingContent.length &&
      streamingContent.length > 0
    ) {
      // Finished typing
      setIsTyping(false);
    }

    previousContentRef.current = streamingContent;

    // Cleanup
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [streamingContent, displayedText]);

  // Calculate offset to push popup outside the circle
  // Convert angle to radians (angle is in degrees, -90 offset to start from top)
  const radian = ((angle - 90) * Math.PI) / 180;

  // Calculate direction vector (pointing outward from center)
  const offsetDistance = 0; // Distance in pixels to push popup outside
  const offsetX = Math.cos(radian) * offsetDistance;
  const offsetY = Math.sin(radian) * offsetDistance;

  // Determine placement based on angle quadrant
  const normalizedAngle = ((angle % 360) + 360) % 360;
  let placement: "top" | "bottom" | "left" | "right" = "top";

  if (normalizedAngle >= 45 && normalizedAngle < 135) {
    placement = "right";
  } else if (normalizedAngle >= 135 && normalizedAngle < 225) {
    placement = "bottom";
  } else if (normalizedAngle >= 225 && normalizedAngle < 315) {
    placement = "left";
  } else {
    placement = "top";
  }

  // Show popup only when there's streaming content
  const hasContent = Boolean(streamingContent && streamingContent.length > 0);

  return (
    <PopupGateway
      placement={placement}
      offset={[offsetX, offsetY]}
      interactive={true}
      visible={hasContent}
      html={
        hasContent ? (
          <div className={styles.popup}>
            <div className={styles.popupHeader}>
              <span
                className={`${styles.speakingDot} ${
                  isSpeaking ? styles.active : ""
                }`}
              />
              <span className={styles.speakerName}>{name}</span>
            </div>
            <div className={styles.popupContent}>
              {displayedText}
              {isTyping && <span className={styles.cursor}>|</span>}
            </div>
          </div>
        ) : null
      }
    >
      <div className={`${styles.agent} ${isSpeaking ? styles.speaking : ""} `}>
        <img
          src={iconUrl}
          alt={name}
          className={`${styles.icon} ${isSpeaking ? styles.bigIcon : ""} ${
            isSpeaking ? styles.pulse : ""
          }`}
        />
        <div className={styles.name}>{name}</div>
        {phase === "voting" && voteCast && voteCast.vote === "out" && (
          <div className={styles.voteOutWrapper}>
            <VoteOut visible={true} reasoning={voteCast.reasoning} />
          </div>
        )}
        {phase === "voting" && voteCast && voteCast.vote === "in" && (
          <div className={styles.voteInWrapper}>
            <VoteIn visible={true} reasoning={voteCast.reasoning} />
          </div>
        )}
      </div>
    </PopupGateway>
  );
}
