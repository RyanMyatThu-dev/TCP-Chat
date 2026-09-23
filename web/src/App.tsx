import { useState } from "react";
import Command from "./Command";
import Cursor from "./Cursor";
import Terminal from "./Terminal";
import { install, invitation, repository, uvCommands } from "./commands";

export default function App() {
  const [platform, setPlatform] = useState<"unix" | "windows">("unix");
  const [path, setPath] = useState<"host" | "join">("host");
  const [code, setCode] = useState("");
  const normalized = invitation(code);
  return (
    <>
      <Cursor />
      <a className="skip-link" href="#install">
        Skip to installation
      </a>
      <header className="site-header">
        <a href="#" className="wordmark" aria-label="Neon Chat home">
          <span className="brand-mark">N</span> NEON
          <span className="slash">/</span>CHAT
        </a>
        <nav aria-label="Main navigation">
          <a href="#install">Get connected</a>
          <a href="#field-notes">Field notes</a>
          <a href={repository} target="_blank" rel="noreferrer">
            Source ↗
          </a>
        </nav>
        <span className="header-note">TERMINAL COMMUNICATIONS / V0.2</span>
      </header>
      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="signal-dot" /> A PRIVATE CORNER OF THE INTERNET
            </div>
            <h1 id="hero-title">
              A little signal
              <br />
              in the <em>noise.</em>
              <span className="title-square" aria-hidden="true" />
            </h1>
            <p>
              Your people. Your terminal. One room code.
              <br />
              Make a temporary space for a conversation that
              <br className="desktop-break" /> doesn’t need another feed.
            </p>
            <div className="hero-actions">
              <a className="primary" href="#install">
                Enter the terminal <span>↗</span>
              </a>
              <span className="micro">
                INSTALL ONCE.
                <br />
                MEET WHENEVER IT’S ONLINE.
              </span>
            </div>
            <div className="hero-foot">
              <span>01 / INSTALL</span>
              <span>02 / INVITE</span>
              <span>03 / TALK</span>
            </div>
          </div>
          <div className="hero-visual">
            <div className="visual-coordinate">
              CHANNEL_001 <span>ROOM / 001</span>
            </div>
            <div className="orbital" aria-hidden="true">
              <div className="orbit orbit-one" />
              <div className="orbit orbit-two" />
              <div className="orbit orbit-three" />
              <span className="orbital-core">
                N<span>_</span>
              </span>
              <i className="satellite" />
              <div className="axis axis-x" />
              <div className="axis axis-y" />
            </div>
            <Terminal />
            <div className="visual-caption">
              <span>NO FEED. NO PROFILE. JUST A ROOM.</span>
              <span>↙ SCROLL TO CONNECT</span>
            </div>
          </div>
        </section>
        <div className="feature-strip">
          <span>
            <i>↗</i> CODE-ONLY INVITATIONS
          </span>
          <span>
            <i>⌁</i> VERIFIED TLS
          </span>
          <span>
            <i>⊘</i> NO SAVED CHAT HISTORY
          </span>
          <span>
            <i>⌘</i> BUILT FOR YOUR TERMINAL
          </span>
        </div>
        <section id="install" className="setup" aria-labelledby="setup-title">
          <div className="section-heading">
            <div>
              <div className="eyebrow">CONNECTION MANUAL / 001</div>
              <h2 id="setup-title">
                From zero to <span>hello.</span>
              </h2>
            </div>
            <p>
              Three steps. One shared space.
              <br />
              Keep this page open beside your terminal.
            </p>
          </div>
          <div className="steps">
            <article className="step">
              <div className="step-number">
                01<span>SETUP</span>
              </div>
              <div className="step-content">
                <h3>Give your terminal the tools.</h3>
                <p>
                  Install{" "}
                  <a
                    href="https://docs.astral.sh/uv/getting-started/installation/"
                    target="_blank"
                    rel="noreferrer"
                  >
                    uv ↗
                  </a>
                  , the package installer. Already have it? Jump to step 02.
                </p>
                <div
                  className="segmented"
                  role="group"
                  aria-label="Operating system"
                >
                  <button
                    aria-pressed={platform === "unix"}
                    onClick={() => setPlatform("unix")}
                  >
                    macOS / Linux
                  </button>
                  <button
                    aria-pressed={platform === "windows"}
                    onClick={() => setPlatform("windows")}
                  >
                    Windows
                  </button>
                </div>
                <Command
                  text={uvCommands[platform]}
                  label="Copy uv installation command"
                />
                <p className="hint">
                  Run in{" "}
                  {platform === "windows" ? "PowerShell" : "your terminal"}.
                  This downloads and runs uv’s official installer. Then open a
                  new terminal.
                </p>
              </div>
            </article>
            <article className="step">
              <div className="step-number">
                02<span>INSTALL</span>
              </div>
              <div className="step-content">
                <h3>Meet your new command.</h3>
                <p>
                  Install NEON CHAT once. uv manages Python and the app’s
                  environment for you.
                </p>
                <Command
                  text={install}
                  label="Copy Neon Chat installation command"
                />
                <p className="hint">
                  If the command isn’t found afterward, run{" "}
                  <code>uv tool update-shell</code> and reopen your terminal.
                </p>
              </div>
            </article>
            <article className="step">
              <div className="step-number">
                03<span>CONNECT</span>
              </div>
              <div className="step-content">
                <h3>Bring your people in.</h3>
                <div
                  className="path-picker"
                  role="group"
                  aria-label="Choose your connection path"
                >
                  <button
                    aria-pressed={path === "host"}
                    onClick={() => setPath("host")}
                  >
                    <span>↗</span>
                    <b>Create a room</b>
                    <small>I’m sending the invite</small>
                  </button>
                  <button
                    aria-pressed={path === "join"}
                    onClick={() => setPath("join")}
                  >
                    <span>↙</span>
                    <b>Join a friend</b>
                    <small>I have a room code</small>
                  </button>
                </div>
                {path === "host" ? (
                  <div className="path-panel">
                    <Command text="neon-chat host" />
                    <p>
                      Choose an alias. Share the join command shown in your
                      terminal with your friends. Keep your terminal connected
                      to keep the room open.
                    </p>
                    <div className="invitation-example">
                      <span>EXAMPLE INVITATION</span>
                      <code>neon-chat join ABCD-1234-EFGH</code>
                      <small>Your terminal generates your real code.</small>
                    </div>
                  </div>
                ) : (
                  <div className="path-panel">
                    <label htmlFor="room-code">Your friend’s room code</label>
                    <input
                      id="room-code"
                      value={code}
                      onChange={(event) => setCode(event.target.value)}
                      placeholder="XXXX-XXXX-XXXX"
                      autoComplete="off"
                      spellCheck={false}
                      maxLength={32}
                      aria-describedby="code-hint"
                      aria-invalid={Boolean(code && !normalized)}
                    />
                    <p id="code-hint" className="hint">
                      {code && !normalized
                        ? "Use all 12 characters from your friend’s invitation."
                        : "Your code stays in this page. It is never sent to a server."}
                    </p>
                    {normalized && (
                      <Command
                        text={`neon-chat join ${normalized}`}
                        label="Copy your join command"
                      />
                    )}
                    <p>
                      Run the command in your terminal, choose your alias, and
                      say hello. Your friend must still be hosting.
                    </p>
                  </div>
                )}
              </div>
            </article>
          </div>
        </section>
        <section
          className="field-notes"
          id="field-notes"
          aria-labelledby="notes-title"
        >
          <div>
            <div className="eyebrow">GOOD TO KNOW / 002</div>
            <h2 id="notes-title">
              Small rooms.
              <br />
              <span>Clear boundaries.</span>
            </h2>
            <p>
              Built for a moment with friends.
              <br />
              Here’s how that moment works.
            </p>
          </div>
          <div className="notes">
            <details open>
              <summary>
                <span>01</span> The host holds the room open.<b>+</b>
              </summary>
              <p>
                When the host leaves, everyone disconnects and the invitation
                expires. Guests can leave without closing the room. Use{" "}
                <code>/invite</code> to see your code again and{" "}
                <code>/quit</code> to leave.
              </p>
            </details>
            <details>
              <summary>
                <span>02</span> A code is your invitation.<b>+</b>
              </summary>
              <p>
                Anyone with the app can host. Anyone with your code can join
                your room, so share it privately. Aliases are display names, not
                verified identities.
              </p>
            </details>
            <details>
              <summary>
                <span>03</span> Encrypted links. Honest limits.<b>+</b>
              </summary>
              <p>
                Verified TLS protects traffic between you and the server. This
                is not end-to-end encryption: the server can read messages. No
                chat history is saved by the service; participants can keep
                their own copies.
              </p>
            </details>
            <details>
              <summary>
                <span>04</span> The service takes breaks.<b>+</b>
              </summary>
              <p>
                The AWS instance stops after roughly three hours to limit costs.
                If it’s offline, ask the operator to start it. Joining from this
                page cannot wake the server or open your terminal.
              </p>
            </details>
          </div>
        </section>
        <section className="closing">
          <span className="brand-mark">N</span>
          <h2>
            Less scrolling.
            <br />
            More <em>talking.</em>
          </h2>
          <a className="primary" href="#install">
            Get connected <span>↗</span>
          </a>
          <span className="closing-index">
            END OF TRANSMISSION / BEGIN YOURS
          </span>
        </section>
      </main>
      <footer>
        <a className="wordmark" href="#">
          NEON / CHAT
        </a>
        <span>A LITTLE SIGNAL IN THE NOISE.</span>
        <a href={repository} target="_blank" rel="noreferrer">
          Open source ↗
        </a>
      </footer>
    </>
  );
}
