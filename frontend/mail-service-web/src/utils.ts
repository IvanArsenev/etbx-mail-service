import { UserMe } from "./api/UserApi";

export const checkAuth = async () => {
  const me = await UserMe();
  return me;
}