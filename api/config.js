export default function handler(req, res) {
  res.setHeader("Content-Type", "application/javascript");
  res.send(`
    window.ENV = {
      TWITCH_CHANNEL: "${process.env.TWITCH_CHANNEL}",
      BACKEND_URL: "${process.env.BACKEND_URL}"
    };
  `);
}