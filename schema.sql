-- Table to log active connections
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    status TEXT NOT NULL,  -- e.g., 'active', 'inactive'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to log user logins
CREATE TABLE IF NOT EXISTS logins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to log SSH brute force attempts
CREATE TABLE IF NOT EXISTS ssh_brute_forces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to log UDP flood attempts
CREATE TABLE IF NOT EXISTS udp_floods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to log IP OSINT lookups
CREATE TABLE IF NOT EXISTS ip_osint_lookups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    lookup_result TEXT,  -- e.g., 'malicious', 'safe'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
