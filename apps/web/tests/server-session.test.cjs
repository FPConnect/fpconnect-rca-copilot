const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');

const source = ts.transpileModule(fs.readFileSync('src/lib/server-session.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;

function validator(fetch, env = { API_URL: 'https://api.example.test', NODE_ENV: 'production' }) {
  const context = { exports: {}, require: (name) => {
    assert.equal(name, 'server-only'); return {};
  }, process: { env }, fetch, URL, AbortSignal };
  vm.runInNewContext(source, context);
  return context.exports.isValidSession;
}

test('missing and preview tokens never reach the API', async () => {
  const validate = validator(() => assert.fail('unexpected fetch'));
  for (const token of [undefined, '', 'fpconnect-preview-token-master']) {
    assert.equal(await validate(token), false);
  }
});

test('only a verified user allows a session; validation is not cached', async () => {
  const validate = validator(async (url, options) => {
    assert.equal(String(url), 'https://api.example.test/auth/me');
    assert.equal(options.headers.Authorization, 'Bearer synthetic-test-token');
    assert.equal(options.cache, 'no-store');
    assert.equal(options.redirect, 'error');
    return { ok: true, json: async () => ({ id: 1 }) };
  });
  assert.equal(await validate('synthetic-test-token'), true);
});

test('expired, invalid, inactive, malformed and unavailable sessions fail closed', async () => {
  const cases = [
    async () => ({ ok: false, status: 401 }),
    async () => ({ ok: false, status: 500 }),
    async () => { throw new Error('network unavailable'); },
    async () => ({ ok: true, json: async () => { throw new Error('invalid JSON'); } }),
    ...[null, {}, { id: '' }, { id: 0 }, { id: 1, is_active: false }].map(
      (user) => async () => ({ ok: true, json: async () => user })
    ),
  ];
  for (const fetch of cases) assert.equal(await validator(fetch)('synthetic-test-token'), false);
});

test('missing API configuration and non-HTTPS production API fail closed', async () => {
  for (const env of [{}, { NODE_ENV: 'production', API_URL: 'http://localhost:8000' }]) {
    assert.equal(await validator(() => assert.fail('unexpected fetch'), env)('synthetic-test-token'), false);
  }
});
