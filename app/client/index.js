const WebSocket = require('ws');
const botId = process.argv[2];
const ws = new WebSocket(`ws://192.168.1.175:8888/ws?botId=${botId}`);

ws.on('open', () => {
    ws.send(JSON.stringify({question: 'something', botId: '123'}));
});

ws.on('message', (data) => {
    console.log(data);
});
