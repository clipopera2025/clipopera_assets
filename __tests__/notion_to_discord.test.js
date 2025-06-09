const mockQuery = jest.fn();

jest.mock('@notionhq/client', () => {
  return {
    Client: jest.fn().mockImplementation(() => ({
      databases: { query: mockQuery },
    })),
  };
});

beforeEach(() => {
  mockQuery.mockReset();
  process.env.NOTION_TOKEN = 'test-token';
  process.env.NOTION_DATABASE_ID = 'dbid';
  process.env.DISCORD_WEBHOOK_URL = 'webhook';
});

test('fetchNotionEntries returns results from Notion API', async () => {
  const sample = { results: [{ id: '1' }] };
  mockQuery.mockResolvedValue(sample);
  const { fetchNotionEntries } = require('../scripts/notion_to_discord');
  const results = await fetchNotionEntries();
  expect(results).toEqual(sample.results);
  expect(mockQuery).toHaveBeenCalledWith({
    database_id: 'dbid',
    filter: {
      property: 'Status',
      rich_text: { equals: 'New' },
    },
  });
});
