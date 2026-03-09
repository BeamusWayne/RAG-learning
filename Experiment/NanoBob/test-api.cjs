const Database = require('better-sqlite3');
const db = new Database('./store/messages.db');

// Get pending messages
const rows = db.prepare(`
  SELECT id, chat_jid, sender, content, timestamp 
  FROM messages 
  WHERE chat_jid = '__tui_chat__' 
  ORDER BY timestamp ASC
`).all();

console.log('Pending messages:', rows.length);
rows.forEach(r => console.log('  ' + r.sender + ': ' + r.content));

// Test Qwen API
const apiKey = 'sk-22daeee007d74be98634b70c63396c5e';
const prompt = rows.map(r => r.sender + ': ' + r.content).join('\n');

console.log('\nSending to Qwen API...');

fetch('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: 'Bearer ' + apiKey,
  },
  body: JSON.stringify({
    model: 'qwen-plus',
    messages: [
      { role: 'system', content: 'You are Bob, a helpful AI assistant.' },
      { role: 'user', content: prompt },
    ],
    temperature: 0.7,
    max_tokens: 1024,
  }),
})
.then(r => r.json())
.then(data => {
  const reply = data.choices?.[0]?.message?.content || 'No response';
  console.log('\nQwen response:');
  console.log(reply);

  // Store bot response
  const botId = 'bot_' + Date.now();
  const botTs = new Date().toISOString();
  db.prepare(`
    INSERT INTO messages (id, chat_jid, sender, sender_name, content, timestamp, is_from_me, is_bot_message)
    VALUES (?, '__tui_chat__', 'Bob', 'NanoBob', ?, ?, 1, 1)
  `).run(botId, reply, botTs);

  console.log('\nResponse stored in database');
  db.close();
})
.catch(err => console.error('Error:', err));
