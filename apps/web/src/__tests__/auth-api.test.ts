import { api } from "@/services/api";

describe("authentication API", () => {
  const originalFetchDescriptor = Object.getOwnPropertyDescriptor(globalThis, "fetch");
  const fetchMock = jest.fn<ReturnType<typeof fetch>, Parameters<typeof fetch>>();

  beforeEach(() => {
    Object.defineProperty(globalThis, "fetch", {
      configurable: true,
      value: fetchMock,
      writable: true,
    });
    fetchMock.mockReset();
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
  });

  afterAll(() => {
    if (originalFetchDescriptor) {
      Object.defineProperty(globalThis, "fetch", originalFetchDescriptor);
    } else {
      Reflect.deleteProperty(globalThis, "fetch");
    }
  });

  it("propagates login connection failures instead of creating a local session", async () => {
    await expect(api.login({ email: "user@example.com", password: "password" }))
      .rejects.toThrow("Failed to fetch");
    expect(localStorage.getItem("auth_token")).toBeNull();
  });

  it("propagates verification-code connection failures instead of reporting success", async () => {
    await expect(api.sendVerificationCode({
      email: "user@example.com",
      phone_number: "+15555550123",
    })).rejects.toThrow("Failed to fetch");
  });

  it("propagates SMS notification failures instead of simulating delivery", async () => {
    await expect(api.sendSmsNotification("SMS test"))
      .rejects.toThrow("Failed to fetch");
  });
});
