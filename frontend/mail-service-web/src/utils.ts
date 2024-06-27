import { UserMe } from "./api/UserApi/index.ts";

export const checkAuth = async () => {
  const me = await UserMe();
  console.log(me);
  return me;
}