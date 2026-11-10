import { useEffect, useLayoutEffect, useState } from "react";
import { ExternalLink } from "lucide-react";
import { useI18n } from "@/i18n";
import { usePageHeader } from "@/contexts/usePageHeader";
import { cn } from "@/lib/utils";
import { PluginSlot } from "@/plugins";

/**
 * Kitsune Agent documentation wiki.
 *
 * The docs site is built from `website/` (baseUrl /kitsune-agent/) and served by the dashboard itself
 * from `hermes_cli/docs_dist` (installed by scripts/fetch-docs-site.sh), so the wiki works offline.
 * When that directory is not installed this page falls back to a pointer at the docs source on GitHub.
 */
export const KITSUNE_DOCS_SOURCE_URL =
  "https://github.com/KingBeam5/kitsune-agent/tree/kitsune/website/docs";
export const KITSUNE_REPO_URL = "https://github.com/KingBeam5/kitsune-agent";

function docsPath(): string {
  const base = (window as unknown as { __HERMES_BASE_PATH__?: string }).__HERMES_BASE_PATH__ ?? "";
  return `${base}/kitsune-agent/`;
}

const DS_BUTTON_OUTLINED_LINK_CN = cn(
  "group relative inline-grid grid-cols-[auto_1fr_auto] items-center",
  "px-[.9em_.75em] py-[1.25em] gap-2",
  "leading-0 font-bold tracking-[0.2em] uppercase",
  "text-midground bg-transparent shadow-midground",
  "shadow-[inset_-1px_-1px_0_0_#00000080,inset_1px_1px_0_0_#ffffff80]",
);

export default function DocsPage() {
  const { t } = useI18n();
  const { setEnd } = usePageHeader();
  const [installed, setInstalled] = useState<boolean | null>(null);

  useEffect(() => {
    let live = true;
    fetch(docsPath(), { method: "HEAD", cache: "no-store" })
      .then((r) => live && setInstalled(r.ok))
      .catch(() => live && setInstalled(false));
    return () => {
      live = false;
    };
  }, []);

  useLayoutEffect(() => {
    setEnd(
      <a
        href={installed ? docsPath() : KITSUNE_DOCS_SOURCE_URL}
        target="_blank"
        rel="noopener noreferrer"
        className={DS_BUTTON_OUTLINED_LINK_CN}
      >
        <ExternalLink className="size-3.5" />
        {t.app.openDocumentation}
      </a>,
    );
    return () => {
      setEnd(null);
    };
  }, [setEnd, t, installed]);

  return (
    <div
      className={cn(
        "flex min-h-0 w-full min-w-0 flex-1 flex-col gap-4",
        "pt-1 sm:pt-2",
      )}
    >
      <PluginSlot name="docs:top" />
      {installed === true && (
        <iframe
          title={t.app.nav.documentation}
          src={docsPath()}
          className={cn(
            "min-h-0 w-full min-w-0 flex-1",
            "rounded-sm border border-current/20",
            // Docusaurus relies on the browser's canvas colour (light by default); force a light
            // scheme + white background so the docs stay readable under any dashboard theme.
            "[color-scheme:light] bg-white",
          )}
          // allow-same-origin is required: Docusaurus needs its own storage and history access and renders
          // blank without it. The docs are served from this origin, so only first-party content built from
          // this repository may be published there (no remote catalogs: see website/scripts/prebuild.mjs).
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        />
      )}
      {installed === false && (
        <div
          className={cn(
            "max-w-2xl space-y-4 p-6",
            "rounded-sm border border-current/20",
          )}
        >
          <h2 className="text-lg font-bold tracking-wide text-midground">
            Kitsune Agent documentation
          </h2>
          <p className="text-text-secondary">
            The documentation site is not installed in this checkout. Run{" "}
            <code>scripts/fetch-docs-site.sh</code> to install it, or read the
            pages on GitHub.
          </p>
          <p className="text-sm text-text-secondary">
            Source:{" "}
            <a
              className="underline"
              href={KITSUNE_DOCS_SOURCE_URL}
              target="_blank"
              rel="noopener noreferrer"
            >
              {KITSUNE_REPO_URL.replace("https://", "")}
            </a>
          </p>
        </div>
      )}
      <PluginSlot name="docs:bottom" />
    </div>
  );
}
