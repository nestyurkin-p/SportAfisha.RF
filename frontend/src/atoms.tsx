import { atomWithStorage } from "jotai/utils";

const accessTokenAtom = atomWithStorage("token", null);
const roleAtom = atomWithStorage("role", "user");

export default { accessTokenAtom, roleAtom };
