# Testes automatizados para o pipeline Vercel

## Unitários e Integração

Adicione ao seu projeto um arquivo `jest.config.js` na raiz do apps/mobile:

```js
module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: ['@testing-library/jest-native/extend-expect'],
  testEnvironment: 'jsdom',
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|expo|expo-router|react-native-reanimated|react-native-gesture-handler|react-native-safe-area-context|react-native-screens|react-native-svg|@expo|lucide-react-native)/)'
  ],
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js',
    '\\.(css|less)$': '<rootDir>/__mocks__/styleMock.js'
  },
  testPathIgnorePatterns: ['/node_modules/', '/e2e/'],
};
```

Crie os mocks em `__mocks__/fileMock.js` e `__mocks__/styleMock.js`:

```js
// fileMock.js
module.exports = '';
```

```js
// styleMock.js
module.exports = {};
```

## E2E (opcional)

Para testes end-to-end, utilize o Detox ou Playwright. Exemplo de script para Playwright:

```json
"scripts": {
  ...,
  "test:e2e": "playwright test"
}
```

E configure o Playwright conforme a documentação oficial.

## Pipeline Vercel

No Vercel, os testes unitários/integração rodam automaticamente se o script `test` estiver definido no `package.json`. Certifique-se de que todas as dependências estejam em `devDependencies` e que o comando `jest` funcione localmente.

## Rodando localmente

1. Instale as dependências:
   ```sh
   npm install
   ```
2. Execute os testes:
   ```sh
   npm test
   ```
3. Para e2e (se configurado):
   ```sh
   npm run test:e2e
   ```

## Observação
- Corrija eventuais erros de dependências ou configuração do Jest conforme o log.
- Para rodar no Vercel, garanta que o comando `npm test` funcione sem erros localmente.