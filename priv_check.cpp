#include <windows.h>
#include <sddl.h>
#include <iostream>
#include <vector>
#include <string>
#define UNLEN 256

void CheckIfAdmin() {
    BOOL isAdmin = FALSE;
    PSID adminGroup = NULL;

    SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;
    if (AllocateAndInitializeSid(&ntAuthority, 2,
        SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS,
        0, 0, 0, 0, 0, 0, &adminGroup))
    {
        CheckTokenMembership(NULL, adminGroup, &isAdmin);
        FreeSid(adminGroup);
    }

    if (isAdmin)
        std::cout << "[+] User is in the Administrators group.\n";
    else
        std::cout << "[-] User is NOT in the Administrators group.\n";
}

void CheckPrivileges() {
    HANDLE token;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token)) {
        std::cerr << "[!] Failed to open process token.\n";
        return;
    }

    DWORD size;
    GetTokenInformation(token, TokenPrivileges, NULL, 0, &size);
    std::vector<BYTE> buffer(size);
    PTOKEN_PRIVILEGES privileges = (PTOKEN_PRIVILEGES)buffer.data();

    if (!GetTokenInformation(token, TokenPrivileges, privileges, size, &size)) {
        std::cerr << "[!] Failed to get token information.\n";
        CloseHandle(token);
        return;
    }

    std::cout << "[*] Checking token privileges:\n";
    for (DWORD i = 0; i < privileges->PrivilegeCount; ++i) {
        LUID luid = privileges->Privileges[i].Luid;
        DWORD nameLen = 0;
        LookupPrivilegeName(NULL, &luid, NULL, &nameLen);
        std::vector<char> nameBuf(nameLen + 1);
        if (LookupPrivilegeName(NULL, &luid, nameBuf.data(), &nameLen)) {
            std::string name(nameBuf.data());

            BOOL enabled = privileges->Privileges[i].Attributes & SE_PRIVILEGE_ENABLED;

            std::cout << "    " << name << " : " << (enabled ? "ENABLED" : "disabled") << "\n";
        }
    }

    CloseHandle(token);
}

int main() {
    std::cout << "[*] Privilege & Admin Check POC\n";

    char username[UNLEN + 1];
    DWORD size = UNLEN + 1;
    if (GetUserNameA(username, &size)) {
        std::cout << "[*] Running as user: " << username << "\n";
    }

    CheckIfAdmin();
    CheckPrivileges();

    return 0;
}
