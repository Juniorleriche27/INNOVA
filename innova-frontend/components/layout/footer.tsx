// innova-frontend/components/layout/footer.tsx
export default function Footer() {
  return (
    <footer className="border-t text-sm text-gray-500 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <span>© {new Date().getFullYear()} INNOVA+</span>
        <span className="hidden sm:inline">v1.0.0</span>
      </div>
    </footer>
  );
}
