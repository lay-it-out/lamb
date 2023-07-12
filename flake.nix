{
  description = "Application packaged using poetry2nix";
  nixConfig.bash-prompt-suffix = "[lamb-dev]> ";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryEnv defaultPoetryOverrides mkPoetryApplication;
        pkgs = nixpkgs.legacyPackages.${system};
        overrides = defaultPoetryOverrides.extend (self: super: {
          open-python = super.open-python.overridePythonAttrs
          (
            old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
            }
          );
        });
      in {
        # For z3, we use the version in nixpkgs, thus avoiding recompilation
        # Therefore, it shall not be listed in poetry, as it's directly managed by nix
        devShells = {
          lamb = (let poetryEnv = mkPoetryEnv {
            projectDir = ./.;
            python = pkgs.python311;
            preferWheels = true;
            extraPackages = (ps: [ ps.z3 ]);
            inherit overrides;
          };
          in poetryEnv.env.overrideAttrs (super: { buildInputs = [ pkgs.graphviz pkgs.jq ]; }));
          default = self.devShells.${system}.lamb;
        };
        packages = {
          lamb = mkPoetryApplication {
            projectDir = ./.;
            python = pkgs.python311;
            preferWheels = true;
            inherit overrides;
            propagatedBuildInputs = [ pkgs.graphviz pkgs.jq pkgs.python311Packages.z3 ];
          };
          default = self.packages.${system}.lamb;
        };
      });
}
