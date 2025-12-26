import { ReactElement } from "react";
import { followCursor } from "tippy.js";

import Tippy, { TippyProps } from "@tippyjs/react/headless";

// Available props here:
// https://atomiks.github.io/tippyjs/v6/all-props/

type Props = { html: ReactElement | null; sameWidth?: boolean } & TippyProps;

export { type Props as PopupGatewayProps };

export default function PopupGateway(props: Props) {
  // Try to get root-popup element, fallback to body if it doesn't exist
  const rootPopupElement =
    document.getElementById("root-popup") || document.body;

  const {
    delay = 0,
    offset = [0, 20],
    html = null,
    placement = "top",
    trigger = "mouseenter",
    interactive = false,
    children,
    className = "",
    disabled = false,
    visible,
    sameWidth = false,
    ...otherOptions
  } = props;

  return (
    <Tippy
      appendTo={rootPopupElement}
      placement={placement}
      delay={delay}
      offset={offset}
      interactive={interactive}
      visible={visible}
      trigger={visible !== undefined ? undefined : trigger}
      {...(sameWidth
        ? {
            popperOptions: {
              modifiers: [
                {
                  name: "sameWidth",
                  enabled: true,
                  fn: ({ state }) => {
                    state.styles.popper.width = `${state.rects.reference.width}px`;
                  },
                  phase: "beforeWrite",
                  requires: ["computeStyles"],
                  effect: ({ state }) => {
                    state.elements.popper.style.width = `${
                      (state.elements.reference as any).clientWidth
                    }px`;
                  },
                },
              ],
            },
          }
        : {})}
      {...otherOptions}
      plugins={[followCursor]}
      render={(attrs) => (
        <div className={className} {...attrs}>
          {disabled ? null : html}
        </div>
      )}
    >
      {children}
    </Tippy>
  );
}
