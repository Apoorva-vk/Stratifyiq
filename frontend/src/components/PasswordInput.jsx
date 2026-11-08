import { useState } from "react";

const EYE = (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const EYE_OFF = (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M17.94 17.94A10.94 10.94 0 0112 19c-7 0-11-7-11-7a19.8 19.8 0 015.06-5.94M9.9 4.24A10.9 10.9 0 0112 4c7 0 11 7 11 7a19.8 19.8 0 01-3.17 4.19M14.12 14.12a3 3 0 11-4.24-4.24" />
    <line x1="1" y1="1" x2="23" y2="23" />
  </svg>
);

/** Password field with a show/hide eye. Accepts the same props as a normal input. */
export default function PasswordInput(props) {
  const [show, setShow] = useState(false);
  const { className = "", ...rest } = props;
  return (
    <span className="pw-wrap">
      <input
        {...rest}
        className={`pw-input ${className}`.trim()}
        type={show ? "text" : "password"}
        autoComplete={rest.autoComplete || "current-password"}
      />
      <button
        type="button"
        className="pw-toggle"
        onClick={() => setShow(!show)}
        aria-label={show ? "Hide password" : "Show password"}
        aria-pressed={show}
        title={show ? "Hide password" : "Show password"}
      >
        {show ? EYE_OFF : EYE}
      </button>
    </span>
  );
}
