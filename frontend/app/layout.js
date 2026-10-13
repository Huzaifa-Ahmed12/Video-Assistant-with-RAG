import "./globals.css";

export const metadata = {
  title: "Video Assistant",
  description: "Turn any video or meeting into notes you can chat with.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}