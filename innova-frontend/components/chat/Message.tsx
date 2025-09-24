export default function Message({ role, content }: { role: "user" | "assistant" | "system"; content: string }) {
  const isUser = role === "user";
  return (
    <div className={`rounded p-3 ${isUser ? "bg-blue-100 text-right" : "bg-gray-100 text-left"}`}>
      <div className="text-xs font-semibold text-gray-500 mb-1">{role.toUpperCase()}</div>
      <p className="whitespace-pre-wrap">{content}</p>
    </div>
  );
}
