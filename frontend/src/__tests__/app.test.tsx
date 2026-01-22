/**
 * Basic smoke tests for MoodTune AI
 */

describe('MoodTune AI', () => {
  it('should have a defined environment', () => {
    expect(process.env.NODE_ENV).toBeDefined();
  });

  it('should pass basic arithmetic', () => {
    expect(1 + 1).toBe(2);
  });
});
