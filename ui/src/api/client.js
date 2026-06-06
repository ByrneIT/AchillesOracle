export async function runScan(url) {
	if (!url) {
		throw new Error("No URL provided");
	}

	// POST JSON to the backend /scan endpoint (FastAPI expects { url: str }).
	const resp = await fetch(`/scan`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json"
		},
		body: JSON.stringify({ url })
	});

	if (!resp.ok) {
		const text = await resp.text();
		throw new Error(`Scan request failed: ${resp.status} ${text}`);
	}

	return resp.json();
}

