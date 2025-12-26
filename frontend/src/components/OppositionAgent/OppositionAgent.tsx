import { useState, useEffect, useRef, useMemo } from "react";
import PopupGateway from "../Popup";
import styles from "./OppositionAgent.module.scss";
import AgentIcon from "@/assets/icons/agent-oppossition.svg";

// Import all available icons
import ChatGptIcon from "@/assets/icons/chat-gpt.svg?url";
import ClaudeIcon from "@/assets/icons/claude.svg?url";
import GeminiIcon from "@/assets/icons/gemini.svg?url";
import DeepSeekIcon from "@/assets/icons/deepseek.svg?url";
import GrokIcon from "@/assets/icons/grok.svg?url";

// Map icon names to their imports
const iconMap: Record<string, string> = {
  "chat-gpt": ChatGptIcon,
  "claude": ClaudeIcon,
  "gemini": GeminiIcon,
  "deepseek": DeepSeekIcon,
  "grok": GrokIcon,
};

interface OppositionAgentProps {
  id?: string;
  name: string;
  icon?: string;
  isActive?: boolean;
  isSpeaking?: boolean;
  streamingContent?: string;
}

export function OppositionAgent({ 
  name,
  icon,
  isSpeaking = false,
  streamingContent = "",
}: OppositionAgentProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const previousContentRef = useRef("");

  // Get icon URL - use configured icon if available, otherwise fallback to default
  // Note: Unlike PropositionAgent, OppositionAgent doesn't have an "active" variant,
  // so we use the custom icon even when speaking (the pulse animation provides visual feedback)
  const iconUrl = useMemo(() => {
    // Always prefer custom icon if provided and exists in map
    if (icon && typeof icon === 'string' && icon.trim() !== '' && iconMap[icon]) {
      return iconMap[icon];
    }
    // Fallback to default icon
    return AgentIcon;
  }, [icon, isSpeaking]);

  // Typing animation effect
  useEffect(() => {
    // Reset if content changed completely (new message)
    if (streamingContent !== previousContentRef.current) {
      // If it's a completely new message (not just more content), reset
      if (streamingContent.length < previousContentRef.current.length || 
          !streamingContent.startsWith(previousContentRef.current)) {
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
    } else if (displayedText.length === streamingContent.length && streamingContent.length > 0) {
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

  // Show popup only when there's streaming content
  const hasContent = Boolean(streamingContent && streamingContent.length > 0);

  return (
    <PopupGateway
      placement="top"
      offset={[40, -40]}
      interactive={true}
      visible={hasContent}
      html={
        hasContent ? (
          <div className={styles.popup}>
            <div className={styles.popupHeader}>
              <span className={`${styles.speakingDot} ${isSpeaking ? styles.active : ''}`} />
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
      <div className={`${styles.agent} ${isSpeaking ? styles.speaking : ''}`}>
        <img src={iconUrl} alt={name} className={`${styles.icon} ${isSpeaking ? styles.bigIcon : ""} ${
            isSpeaking ? styles.pulse : ""
          }`} />
        <div className={styles.name}>{name}</div>
      </div>
    </PopupGateway>
  );
}

