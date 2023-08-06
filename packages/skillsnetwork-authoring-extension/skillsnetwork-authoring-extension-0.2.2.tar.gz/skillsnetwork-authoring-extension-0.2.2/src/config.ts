export const ATLAS_BASE_URL = (): string => {
  const currentURL = window.location.href;

  const params = new URL(currentURL).searchParams;
  const base_url: string | null = params.get('atlas_base_url');
  if (base_url === null) {
    return process.env.ATLAS_BASE_URL ??
      'https://author.skills.network/atlas'
      // 'https://author.staging.skills.network/atlas'
  }

  return base_url;
};

/**
 * Extracts the session token. Will first try to get a token via the URL, if none was found then try to get the token via cookie.
 *
 * @returns token
 */
export const ATLAS_TOKEN = (): string => {

  const currentURL = window.location.href;

  const params = new URL(currentURL).searchParams;
  let token: string | null = params.get('token');
  if (token === null) {
    // Try getting it from cookie
    const COOKIE_NAME: string = process.env.ATLAS_TOKEN_COOKIE_NAME ?? 'atlas_token';
    const reg: RegExp = new RegExp(`(^| )${COOKIE_NAME}=([^;]+)`);
    let match = reg.exec(document.cookie);
    // If found then set that as our token o/w set it as empty str for now
    (match !== null) ? token = match[2] : token = 'NO_TOKEN'
  }

  if (token === null || token === 'NO_TOKEN'){
    // If no token was found in the URL or cookies, the author is in their local env (hopefully...)
    Globals.author_env = 'local'
    // Persist this token
    Globals.token = token;
  }

  return token;
};

// Global token variable that will store the
export class Globals {
  public static token: string;
  public static author_env: string;
}
