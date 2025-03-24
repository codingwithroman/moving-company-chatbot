    export default async function handler(req, res) {
    if (req.method === 'POST') {
        try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(req.body),
        });

        if (!response.ok) {
            throw new Error('Failed to fetch from backend');
        }

        const data = await response.json();
        res.status(200).json(data);
        } catch (error) {
        console.error('Error in API route:', error);
        res.status(500).json({ error: 'Error processing request' });
        }
    } else {
        res.setHeader('Allow', ['POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
    }