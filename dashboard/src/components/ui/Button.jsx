import { isValidElement, cloneElement } from "react";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  className = "",
  ...props
}) {
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-500 text-white",
    secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700",
    danger: "bg-red-600/10 hover:bg-red-600/20 text-red-400 border border-red-600/30",
    ghost: "hover:bg-slate-800 text-slate-300",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2.5 text-sm",
    lg: "px-5 py-3 text-sm",
  };

  // Terima icon dalam 2 bentuk: component reference (icon={Save})
  // ATAU element yang sudah jadi (icon={<Save size={16} />})
  let renderedIcon = null;
  if (Icon) {
    renderedIcon = isValidElement(Icon)
      ? cloneElement(Icon, { size: Icon.props.size ?? 16 })
      : <Icon size={16} />;
  }

  return (
    <button
      className={`
        inline-flex items-center gap-2 rounded-xl font-medium
        transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]} ${className}
      `}
      {...props}
    >
      {renderedIcon}
      {children}
    </button>
  );
}