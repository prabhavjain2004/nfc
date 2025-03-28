class NFCReader {
    constructor(options = {}) {
        this.onCardDetected = options.onCardDetected || (() => {});
        this.onError = options.onError || console.error;
        this.onReading = options.onReading || (() => {});
        this.onReadingError = options.onReadingError || console.error;
        this.reader = null;
        this.isReading = false;
    }

    async init() {
        try {
            if (!('NDEFReader' in window)) {
                throw new Error('NFC reading is not supported in this browser');
            }

            this.reader = new NDEFReader();
            await this.reader.scan();
            
            this.reader.addEventListener("reading", ({ message, serialNumber }) => {
                this.onReading({
                    serialNumber,
                    message: this._parseNDEFMessage(message)
                });
            });

            this.reader.addEventListener("readingerror", () => {
                this.onReadingError(new Error('Error reading NFC tag'));
            });

            return true;
        } catch (error) {
            this.onError(error);
            return false;
        }
    }

    _parseNDEFMessage(message) {
        const records = [];
        for (const record of message.records) {
            records.push({
                recordType: record.recordType,
                mediaType: record.mediaType,
                data: record.data
            });
        }
        return records;
    }

    async write(data) {
        try {
            if (!this.reader) {
                throw new Error('NFC Reader not initialized');
            }

            await this.reader.write(data);
            return true;
        } catch (error) {
            this.onError(error);
            return false;
        }
    }

    stop() {
        if (this.reader) {
            this.reader.stop();
            this.reader = null;
        }
    }
}

// Helper function to format card data for writing
function formatCardData(cardNumber, balance = 0) {
    return {
        records: [{
            recordType: "text",
            data: JSON.stringify({
                cardNumber,
                balance,
                lastUpdated: new Date().toISOString()
            })
        }]
    };
}

// Example usage:
/*
const nfcReader = new NFCReader({
    onCardDetected: (card) => {
        console.log('Card detected:', card);
    },
    onReading: ({ serialNumber, message }) => {
        console.log('Card read:', { serialNumber, message });
    },
    onError: (error) => {
        console.error('NFC Error:', error);
    }
});

// Initialize NFC reader
async function startNFCReader() {
    const success = await nfcReader.init();
    if (success) {
        console.log('NFC Reader initialized successfully');
    }
}

// Write data to NFC card
async function writeToCard(cardNumber, balance) {
    const data = formatCardData(cardNumber, balance);
    const success = await nfcReader.write(data);
    if (success) {
        console.log('Data written successfully');
    }
}

// Stop NFC reader
function stopNFCReader() {
    nfcReader.stop();
    console.log('NFC Reader stopped');
}
*/
