import { SecureSessionStore } from "./session";

interface Storage {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

const KEY = "fpconnect.mobile.access.v1";
const PREFIX = "fpconnect.mobile.session.";
let sequence = 0;

async function newSlot(storage: Storage): Promise<string> {
  let slot: string;
  do {
    slot = `${PREFIX}${Date.now()}.${++sequence}`;
  } while (await storage.getItem(slot) !== null);
  return slot;
}

function slotStore(storage: Storage, slot: string, published: boolean): SecureSessionStore {
  return {
    getItem: () => storage.getItem(slot),
    async setItem(value) {
      await storage.setItem(slot, value);
      if (!published) {
        await storage.setItem(KEY, `slot:${slot}`);
        published = true;
      }
    },
    async removeItem() {
      await storage.removeItem(slot);
      // Sign-in is disabled while this removal runs, so a new pointer cannot
      // be published between this read and delete in the same provider.
      if (await storage.getItem(KEY) === `slot:${slot}`) await storage.removeItem(KEY);
    },
    removeStaleItem: () => storage.removeItem(slot),
  };
}

export async function createSessionStore(storage: Storage): Promise<SecureSessionStore> {
  return slotStore(storage, await newSlot(storage), false);
}

export async function openSessionStore(storage: Storage): Promise<SecureSessionStore | null> {
  const active = await storage.getItem(KEY);
  if (!active) return null;
  if (active.startsWith(`slot:${PREFIX}`)) return slotStore(storage, active.slice(5), true);
  // Migrate the prior access-only or token-pair value without touching drafts.
  const slot = await newSlot(storage);
  await storage.setItem(slot, active);
  await storage.setItem(KEY, `slot:${slot}`);
  return slotStore(storage, slot, true);
}
