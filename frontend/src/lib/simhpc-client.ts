import { api } from './api';

export const simhpcFetch = (endpoint: string, options: any = {}) => {
  return api.fetch(endpoint, options);
};
